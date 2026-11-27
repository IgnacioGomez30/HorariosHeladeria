"""Copia coherente de SQLite previa a una migración."""

import hashlib
import json
import os
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from .esquema import Modo, verificar_base


def _lectura(ruta: Path) -> sqlite3.Connection:
    return sqlite3.connect(ruta.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)


def _estado(conexion: sqlite3.Connection) -> dict:
    esquema, = conexion.execute("PRAGMA user_version").fetchone()
    fila = conexion.execute("""
        SELECT dataset_id, mode, config_head_id, schedule_head_id, input_epoch
        FROM app_state WHERE singleton = 1
    """).fetchone()
    if fila is None:
        raise ValueError("Falta la identidad del conjunto para el respaldo.")
    conjunto, modo, cabeza_config, cabeza_horario, epoca = fila
    return {
        "datasetId": conjunto,
        "mode": modo,
        "schemaVersion": esquema,
        "configHeadId": cabeza_config,
        "scheduleHeadId": cabeza_horario,
        "inputEpoch": epoca,
    }


def crear_respaldo(origen: Path, directorio: Path) -> Path:
    """Genera y verifica el .hhbackup antes de que el migrador cambie el esquema.

    El migrador conserva BEGIN IMMEDIATE en su propia conexión. La copia lee
    una instantánea comprometida con otra conexión, incluso en modo journal DELETE.
    """
    directorio.mkdir(parents=True, exist_ok=True, mode=0o700)
    with TemporaryDirectory(dir=directorio, prefix=".pre-migracion-") as temporal:
        imagen = Path(temporal) / "schedule.sqlite"
        with closing(_lectura(origen)) as fuente, closing(sqlite3.connect(imagen)) as copia:
            fuente.execute("BEGIN")
            estado = _estado(fuente)
            fuente.backup(copia)

        with closing(_lectura(imagen)) as copia:
            verificar_base(copia, Modo(estado["mode"]), estado["schemaVersion"])
            if _estado(copia) != estado:
                raise ValueError("El respaldo difiere del estado de origen.")

        with imagen.open("rb") as archivo:
            digest = hashlib.file_digest(archivo, "sha256").hexdigest()
        manifiesto = {
            "format": "heladeria-horarios.backup",
            "formatVersion": "1.0",
            "createdAt": datetime.now(UTC).isoformat(),
            "appVersion": version("horarios-heladeria"),
            **estado,
            "sizeBytes": imagen.stat().st_size,
            "sha256": digest,
        }
        contenedor = Path(temporal) / "copia.hhbackup"
        contenedor.touch(mode=0o600, exist_ok=False)
        with ZipFile(contenedor, "w", compression=ZIP_DEFLATED) as paquete:
            paquete.write(imagen, arcname="schedule.sqlite")
            paquete.writestr("manifest.json", json.dumps(manifiesto))
        with ZipFile(contenedor) as paquete:
            if sorted(paquete.namelist()) != ["manifest.json", "schedule.sqlite"]:
                raise ValueError("Los miembros del respaldo son incorrectos.")
            if json.loads(paquete.read("manifest.json")) != manifiesto:
                raise ValueError("El manifiesto del respaldo difiere del original.")
            with paquete.open("schedule.sqlite") as archivo:
                if hashlib.file_digest(archivo, "sha256").hexdigest() != digest:
                    raise ValueError("El contenido del respaldo difiere de la imagen verificada.")

        # Publicar solo el contenedor completo, sin reemplazar una copia previa.
        with contenedor.open("r+b") as archivo:
            os.fsync(archivo.fileno())
        destino = directorio / f"pre-migracion-v{estado['schemaVersion']}-{uuid4().hex}.hhbackup"
        os.link(contenedor, destino)
        if hasattr(os, "O_DIRECTORY"):
            descriptor = os.open(directorio, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return destino
