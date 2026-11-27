"""Apertura exclusiva y actualización transaccional de los almacenes locales."""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .esquema import ID_APLICACION, MIGRACIONES, ErrorBase, Modo, verificar_base
from .respaldo import crear_respaldo


def ruta_base(raiz: Path, modo: Modo) -> Path:
    """La raíz es el directorio de datos local elegido por la instalación."""
    return Path(raiz) / Modo(modo).value.lower() / "schedule.sqlite"


@contextmanager
def _escritor_exclusivo(ruta: Path) -> Iterator[None]:
    # El archivo se conserva. El SO libera el bloqueo al cerrar o morir el proceso.
    with ruta.open("a+b") as archivo:
        try:
            if os.name == "nt":
                import msvcrt

                archivo.seek(0)
                msvcrt.locking(archivo.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(archivo, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ErrorBase("No se pudo tomar el bloqueo de escritura del almacén.") from exc
        yield


def _preparar(conexion: sqlite3.Connection, ruta: Path, modo: Modo) -> None:
    conexion.execute("PRAGMA trusted_schema = OFF")
    conexion.execute("PRAGMA foreign_keys = ON")
    if conexion.execute("PRAGMA foreign_keys").fetchone() != (1,):
        raise ErrorBase("SQLite no pudo activar las claves foráneas.")
    conexion.execute("PRAGMA synchronous = FULL")
    conexion.execute("BEGIN IMMEDIATE")
    version = conexion.execute("PRAGMA user_version").fetchone()[0]
    actual = len(MIGRACIONES)
    if not 0 <= version <= actual:
        raise ErrorBase(f"Versión de esquema {version} incompatible con esta aplicación ({actual}).")

    if version:
        verificar_base(conexion, modo, version)
    elif (conexion.execute("SELECT 1 FROM sqlite_schema LIMIT 1").fetchone()
          or conexion.execute("PRAGMA application_id").fetchone()[0] != 0):
        raise ErrorBase("El archivo contiene un esquema desconocido sin versión.")

    if version == actual:
        conexion.commit()
        return

    respaldo = None
    if version:
        # El bloqueo de escritura ya está tomado. La copia usa una conexión lectora.
        respaldo = crear_respaldo(ruta, ruta.parent / "respaldos")

    try:
        for numero in range(version + 1, actual + 1):
            MIGRACIONES[numero - 1](conexion)
            ahora = datetime.now(UTC).isoformat()
            if numero == 1:
                conexion.execute(f"PRAGMA application_id = {ID_APLICACION}")
                conexion.execute(
                    "INSERT INTO app_state(singleton, dataset_id, mode, created_at) VALUES(1,?,?,?)",
                    (str(uuid4()), modo.value, ahora),
                )
            conexion.execute(
                "INSERT INTO schema_migration(version, applied_at) VALUES(?,?)", (numero, ahora)
            )
            conexion.execute(f"PRAGMA user_version = {numero}")
        verificar_base(conexion, modo, actual)
        conexion.commit()
    except Exception as exc:
        detalle = f" Copia previa: {respaldo}." if respaldo else ""
        raise ErrorBase(f"Falló la migración desde la versión {version}.{detalle}") from exc


@contextmanager
def abrir_base(raiz: Path, modo: Modo) -> Iterator[sqlite3.Connection]:
    """Abre o crea el conjunto solicitado, migra al esquema vigente y cierra al salir."""
    modo = Modo(modo)
    ruta = ruta_base(raiz, modo)
    ruta.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with _escritor_exclusivo(ruta.parent / "escritor.lock"):
        with closing(sqlite3.connect(ruta, timeout=3)) as conexion:
            try:
                _preparar(conexion, ruta, modo)
            except (sqlite3.Error, OSError) as exc:
                raise ErrorBase(f"No se pudo preparar el almacén {modo.value}: {exc}") from exc
            # Una excepción revierte el trabajo pendiente. closing libera la conexión
            # incluso si el fallo ocurrió durante la preparación previa al yield.
            with conexion:
                yield conexion
