import hashlib
import json
import sqlite3
from contextlib import closing
from zipfile import ZipFile

import pytest

from heladeria.infraestructura.base import Modo, abrir_base, ruta_base
from heladeria.infraestructura.respaldo import crear_respaldo


def test_respaldo_recupera_solo_el_estado_confirmado(tmp_path):
    raiz = tmp_path / "perfil"
    with abrir_base(raiz, Modo.DEMO) as base:
        base.execute("INSERT INTO person(person_id) VALUES (?)",
                     ("c3e96fde-7485-458f-88ba-2df672227b96",))
        base.commit()
        dataset, = base.execute("SELECT dataset_id FROM app_state").fetchone()
        esquema, = base.execute("PRAGMA user_version").fetchone()
        # El migrador retiene la reserva de escritura mientras se toma la copia.
        base.execute("BEGIN IMMEDIATE")
        base.execute("INSERT INTO person(person_id) VALUES (?)",
                     ("1bd72148-0b95-4321-bf69-c7a87cbfa50f",))
        ruta = crear_respaldo(ruta_base(raiz, Modo.DEMO), tmp_path / "respaldos")
        base.rollback()

    with ZipFile(ruta) as contenedor:
        assert sorted(contenedor.namelist()) == ["manifest.json", "schedule.sqlite"]
        manifiesto = json.loads(contenedor.read("manifest.json"))
        datos = contenedor.read("schedule.sqlite")
    assert manifiesto["format"] == "heladeria-horarios.backup"
    assert manifiesto["formatVersion"] == "1.0"
    assert manifiesto["schemaVersion"] == esquema
    assert manifiesto["datasetId"] == dataset
    assert manifiesto["mode"] == "DEMO"
    assert manifiesto["scheduleHeadId"] is None
    assert manifiesto["sizeBytes"] == len(datos)
    assert manifiesto["sha256"] == hashlib.sha256(datos).hexdigest()

    recuperada = tmp_path / "recuperada.sqlite"
    recuperada.write_bytes(datos)
    with closing(sqlite3.connect(recuperada.as_uri() + "?mode=ro", uri=True)) as copia:
        assert copia.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert copia.execute("PRAGMA foreign_key_check").fetchall() == []
        assert copia.execute("SELECT person_id FROM person").fetchall() == [
            ("c3e96fde-7485-458f-88ba-2df672227b96",),
        ]


def test_dano_al_empaquetar_conserva_los_respaldos_previos(tmp_path, monkeypatch):
    raiz = tmp_path / "perfil"
    directorio = tmp_path / "respaldos"
    with abrir_base(raiz, Modo.REAL):
        pass
    origen = ruta_base(raiz, Modo.REAL)
    previa = crear_respaldo(origen, directorio)
    contenido_previo = previa.read_bytes()

    def escribir_truncado(contenedor, archivo, arcname):
        contenedor.writestr(arcname, b"datos truncados")

    monkeypatch.setattr(ZipFile, "write", escribir_truncado)
    with pytest.raises(ValueError, match="respaldo"):
        crear_respaldo(origen, directorio)
    assert list(directorio.iterdir()) == [previa]
    assert previa.read_bytes() == contenido_previo
