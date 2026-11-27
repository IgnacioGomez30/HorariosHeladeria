"""Pruebas de actualización del archivo real de SQLite en directorios temporales."""

from contextlib import closing
import shutil
import sqlite3
import subprocess
import sys
from zipfile import ZipFile

import pytest

from heladeria.infraestructura import base


PERSONA_V1 = "cbf65b83-528d-42dd-b62e-4c32ed90bd7c"


def crear_v1(raiz, monkeypatch):
    with monkeypatch.context() as parche:
        parche.setattr(base, "MIGRACIONES", base.MIGRACIONES[:1])
        with base.abrir_base(raiz, base.Modo.DEMO) as conexion:
            conexion.execute("INSERT INTO person(person_id) VALUES (?)", (PERSONA_V1,))
            conexion.commit()
    return base.ruta_base(raiz, base.Modo.DEMO)


def estado(ruta):
    """Lee la versión, el esquema y los datos sin invocar los migradores."""
    with closing(sqlite3.connect(ruta.as_uri() + "?mode=ro", uri=True)) as db:
        assert db.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        return {
            "version": db.execute("PRAGMA user_version").fetchone()[0],
            "aplicacion": db.execute("PRAGMA application_id").fetchone()[0],
            "conjunto": db.execute("SELECT * FROM app_state").fetchall(),
            "catalogo": db.execute(
                "SELECT name, sql FROM sqlite_schema ORDER BY name"
            ).fetchall(),
            "personas": db.execute("SELECT person_id FROM person ORDER BY person_id").fetchall(),
            "historial": db.execute(
                "SELECT version, applied_at FROM schema_migration ORDER BY version"
            ).fetchall(),
        }


def respaldos_de(ruta):
    return sorted((ruta.parent / "respaldos").glob("*.hhbackup"))


def leer_respaldo(archivo, destino):
    with ZipFile(archivo) as contenedor:
        assert sorted(contenedor.namelist()) == ["manifest.json", "schedule.sqlite"]
        destino.write_bytes(contenedor.read("schedule.sqlite"))
    return estado(destino)


def test_migra_v1_con_copia_previa_verificable_y_reabre_sin_repetir(tmp_path, monkeypatch):
    ruta = crear_v1(tmp_path, monkeypatch)
    anterior = estado(ruta)
    assert anterior["version"] == 1
    assert anterior["personas"] == [(PERSONA_V1,)]
    assert respaldos_de(ruta) == []

    with base.abrir_base(tmp_path, base.Modo.DEMO) as conexion:
        assert conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conexion.execute("PRAGMA synchronous").fetchone()[0] == 2
        assert conexion.execute("PRAGMA journal_mode").fetchone()[0] == "delete"

    [respaldo] = respaldos_de(ruta)
    assert leer_respaldo(respaldo, tmp_path / "antes.sqlite") == anterior
    actual = estado(ruta)
    assert actual["version"] == len(base.MIGRACIONES)
    assert actual["personas"] == anterior["personas"]
    assert actual["conjunto"] == anterior["conjunto"]
    assert [v for v, _ in actual["historial"]] == list(range(1, actual["version"] + 1))
    assert actual["historial"][:1] == anterior["historial"]
    with base.abrir_base(tmp_path, base.Modo.DEMO):
        pass
    assert estado(ruta) == actual
    assert respaldos_de(ruta) == [respaldo]


def test_error_ddl_y_dml_revierte_toda_la_actualizacion_y_permite_reintento(tmp_path, monkeypatch):
    ruta = crear_v1(tmp_path, monkeypatch)
    anterior = estado(ruta)
    pasos = []

    def falla_en_ultimo_salto(conexion):
        conexion.execute("CREATE TABLE cambio_parcial(x INTEGER)")
        conexion.execute("DELETE FROM person")
        pasos.append("DDL y DML ejecutados")
        conexion.execute("INSERT INTO tabla_inexistente VALUES (1)")

    with monkeypatch.context() as parche:
        # La prueba incluye un salto exitoso a v2 y un segundo salto fallido.
        parche.setattr(base, "MIGRACIONES", (*base.MIGRACIONES, falla_en_ultimo_salto))
        with pytest.raises(base.ErrorBase):
            with base.abrir_base(tmp_path, base.Modo.DEMO):
                pytest.fail("Una actualización incompleta no puede abrir el repositorio")

    assert pasos == ["DDL y DML ejecutados"]
    assert estado(ruta) == anterior
    [copia] = respaldos_de(ruta)
    assert leer_respaldo(copia, tmp_path / "recuperada.sqlite") == anterior
    with base.abrir_base(tmp_path, base.Modo.DEMO):
        pass
    assert estado(ruta)["personas"] == anterior["personas"]
    assert estado(ruta)["version"] == len(base.MIGRACIONES)


def test_salida_abrupta_a_mitad_de_migracion_recupera_la_base(tmp_path, monkeypatch):
    ruta = crear_v1(tmp_path, monkeypatch)
    anterior = estado(ruta)
    script = """
import os
import sys
from pathlib import Path
from heladeria.infraestructura import base

def interrumpir(conexion):
    conexion.execute("DELETE FROM person")
    conexion.execute("CREATE TABLE cambio_interrumpido(x INTEGER)")
    os._exit(47)

base.MIGRACIONES = (*base.MIGRACIONES[:1], interrumpir)
with base.abrir_base(Path(sys.argv[1]), base.Modo.DEMO):
    raise AssertionError("La migración no se ejecutó")
"""
    proceso = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)], capture_output=True, text=True, timeout=20
    )
    assert proceso.returncode == 47, proceso.stderr
    # Una apertura de lectura/escritura permite a SQLite recuperar un hot journal.
    with closing(sqlite3.connect(ruta)) as conexion:
        conexion.execute("SELECT count(*) FROM person").fetchone()
    assert estado(ruta) == anterior
    [respaldo] = respaldos_de(ruta)
    assert leer_respaldo(respaldo, tmp_path / "pre_corte.sqlite") == anterior


def test_respaldo_imposible_impide_la_migracion(tmp_path, monkeypatch):
    ruta = crear_v1(tmp_path, monkeypatch)
    anterior = estado(ruta)
    directorio = ruta.parent / "respaldos"
    if directorio.is_dir():
        directorio.rmdir()
    directorio.write_text("Ruta deliberadamente ocupada", encoding="utf-8")
    with pytest.raises(base.ErrorBase):
        with base.abrir_base(tmp_path, base.Modo.DEMO):
            pytest.fail("Falta la copia previa obligatoria")
    assert estado(ruta) == anterior


def test_real_y_demo_persisten_en_directorios_independientes(tmp_path):
    for modo in (base.Modo.DEMO, base.Modo.REAL):
        with base.abrir_base(tmp_path, modo) as conexion:
            assert conexion.execute("SELECT mode FROM app_state").fetchone()[0] == modo.value
            if modo is base.Modo.DEMO:
                conexion.execute("INSERT INTO person(person_id) VALUES (?)", (PERSONA_V1,))
                conexion.commit()

    demo = base.ruta_base(tmp_path, base.Modo.DEMO)
    real = base.ruta_base(tmp_path, base.Modo.REAL)
    assert real.parent != demo.parent
    assert estado(demo)["personas"] == [(PERSONA_V1,)]
    assert estado(real)["personas"] == []
    with closing(sqlite3.connect(real)) as conexion:
        id_real = conexion.execute("SELECT dataset_id FROM app_state").fetchone()[0]
    with closing(sqlite3.connect(demo)) as conexion:
        assert conexion.execute("SELECT dataset_id FROM app_state").fetchone()[0] != id_real


def test_base_de_otro_modo_en_la_ruta_real_se_rechaza_antes_de_migrar(tmp_path, monkeypatch):
    demo = crear_v1(tmp_path, monkeypatch)
    real = base.ruta_base(tmp_path, base.Modo.REAL)
    real.parent.mkdir(parents=True)
    shutil.copyfile(demo, real)
    with pytest.raises(base.ErrorBase):
        with base.abrir_base(tmp_path, base.Modo.REAL):
            pytest.fail("No se puede promover una base demo cambiándola de directorio")
    assert estado(real) == estado(demo)
    assert respaldos_de(real) == []


def test_version_futura_no_sufre_downgrade(tmp_path):
    ruta = base.ruta_base(tmp_path, base.Modo.DEMO)
    with base.abrir_base(tmp_path, base.Modo.DEMO) as conexion:
        conexion.execute("PRAGMA user_version = 999")
    anterior = estado(ruta)
    with pytest.raises(base.ErrorBase):
        with base.abrir_base(tmp_path, base.Modo.DEMO):
            pytest.fail("Una base más nueva debe requerir un lector compatible")
    assert estado(ruta) == anterior


def test_archivo_sqlite_ajeno_sin_version_no_se_adopta(tmp_path):
    ruta = base.ruta_base(tmp_path, base.Modo.REAL)
    ruta.parent.mkdir(parents=True)
    with closing(sqlite3.connect(ruta)) as db:
        db.execute("CREATE TABLE otro_proyecto(dato TEXT)")
        db.execute("INSERT INTO otro_proyecto VALUES ('sintetico')")
        db.commit()
    with pytest.raises(base.ErrorBase):
        with base.abrir_base(tmp_path, base.Modo.REAL):
            pytest.fail("No se puede inicializar sobre otra base")
    with closing(sqlite3.connect(ruta)) as db:
        assert db.execute("SELECT name FROM sqlite_schema").fetchall() == [("otro_proyecto",)]
        assert db.execute("SELECT dato FROM otro_proyecto").fetchall() == [("sintetico",)]
        assert db.execute("PRAGMA application_id").fetchone() == (0,)
        assert db.execute("PRAGMA user_version").fetchone() == (0,)


def test_un_escritor_por_conjunto_y_liberacion_al_cerrar(tmp_path):
    with base.abrir_base(tmp_path, base.Modo.DEMO):
        with pytest.raises(base.ErrorBase, match="bloqueo"):
            with base.abrir_base(tmp_path, base.Modo.DEMO):
                pytest.fail("La segunda apertura de la misma base obtuvo acceso de escritura")
        with base.abrir_base(tmp_path, base.Modo.REAL) as real:
            assert real.execute("SELECT mode FROM app_state").fetchone() == ("REAL",)
    with base.abrir_base(tmp_path, base.Modo.DEMO) as demo:
        assert demo.execute("SELECT mode FROM app_state").fetchone() == ("DEMO",)
