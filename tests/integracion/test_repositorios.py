"""Repositorio SQLite sobre archivos descartables, con identidades ficticias."""

from dataclasses import replace
from datetime import date

import pytest

from heladeria.dominio.francos import CupoFrancos
from heladeria.dominio.personas import Persona, Rol
from heladeria.dominio.reglas import ClaseRegla, MetaMinutos, Regla, Vigencia
from heladeria.infraestructura.base import Modo, abrir_base
from heladeria.infraestructura.repositorios import (
    guardar_persona, guardar_reglas, persona_por_id, reglas_de_persona,
)


DIA = date(2027, 2, 1)
CAMBIO = date(2027, 2, 15)


def test_B04_reapertura_preserva_identidad_historia_y_cupos(tmp_path):
    inicial = Persona("Demo Sol", Rol.EMPLEADO, DIA)
    homonimo = Persona("Demo Sol", Rol.PROPIETARIO, DIA)
    nueva = replace(inicial, hasta=date(2027, 3, 1))
    cupos = (
        Regla("francos", 1, Vigencia(DIA, CAMBIO), CupoFrancos({1}, 1)),
        Regla("francos", 2, Vigencia(CAMBIO), CupoFrancos({2}, 1)),
    )
    with abrir_base(tmp_path, Modo.DEMO) as con:
        primera = guardar_persona(con, inicial)
        guardar_persona(con, homonimo)
        guardar_reglas(con, inicial.id, (Regla("francos", 1, Vigencia(DIA), CupoFrancos({1}, 1)),))
        anterior = guardar_persona(con, nueva)
        guardar_reglas(con, inicial.id, cupos)
        meta = Regla("objetivo", 1, Vigencia(DIA), MetaMinutos(360, ClaseRegla.PREFERENCIA))
        guardar_reglas(con, inicial.id, (meta,))

    with abrir_base(tmp_path, Modo.DEMO) as con:
        assert persona_por_id(con, inicial.id, primera) == inicial
        assert persona_por_id(con, homonimo.id, primera) is None
        assert persona_por_id(con, homonimo.id) == homonimo
        assert persona_por_id(con, inicial.id) == nueva
        assert reglas_de_persona(con, inicial.id, "francos") == cupos
        assert reglas_de_persona(con, inicial.id, "francos", anterior)[0].vigencia.hasta is None
        assert reglas_de_persona(con, inicial.id, "objetivo") == (meta,)


def test_B04_regla_incompatible_no_mueve_cabeza_ni_crea_revision(tmp_path):
    persona = Persona("Demo Sol", Rol.EMPLEADO, DIA)
    original = Regla("cuota", 1, Vigencia(DIA), CupoFrancos({1}, 1))
    incompatible = Regla("cuota", 2, Vigencia(CAMBIO), CupoFrancos({2}, 1))
    with abrir_base(tmp_path, Modo.DEMO) as con:
        guardar_persona(con, persona)
        revision = guardar_reglas(con, persona.id, (original,))
        with pytest.raises(ValueError, match="superp"):
            guardar_reglas(con, persona.id, (original, incompatible))
        assert con.execute("SELECT config_head_id, input_epoch FROM app_state").fetchone()[:] == (revision, 2)
        assert con.execute("SELECT COUNT(*) FROM config_revision").fetchone()[0] == 2
        assert reglas_de_persona(con, persona.id, "cuota") == (original,)


def test_B04_copia_previa_y_base_migrada_conservan_la_misma_revision(tmp_path, monkeypatch):
    import sqlite3
    from contextlib import closing
    from zipfile import ZipFile

    from heladeria.infraestructura import base

    persona = Persona("Demo Alba", Rol.EMPLEADO, DIA)
    regla = Regla("francos", 1, Vigencia(DIA), CupoFrancos({1}, 1))
    with monkeypatch.context() as parche:
        parche.setattr(base, "MIGRACIONES", base.MIGRACIONES[:1])
        with abrir_base(tmp_path, Modo.DEMO) as con:
            guardar_persona(con, persona)
            revision = guardar_reglas(con, persona.id, (regla,))

    with abrir_base(tmp_path, Modo.DEMO) as con:
        assert con.execute("PRAGMA user_version").fetchone() == (2,)
        assert persona_por_id(con, persona.id, revision) == persona
        assert reglas_de_persona(con, persona.id, regla.clave) == (regla,)

    [respaldo] = (base.ruta_base(tmp_path, Modo.DEMO).parent / "respaldos").glob("*.hhbackup")
    anterior = tmp_path / "imagen-v1.sqlite"
    with ZipFile(respaldo) as copia:
        anterior.write_bytes(copia.read("schedule.sqlite"))
    with closing(sqlite3.connect(anterior.as_uri() + "?mode=ro", uri=True)) as con:
        assert con.execute("PRAGMA user_version").fetchone() == (1,)
        assert con.execute("SELECT config_head_id FROM app_state").fetchone() == (revision,)
        assert persona_por_id(con, persona.id) == persona
        assert reglas_de_persona(con, persona.id, regla.clave) == (regla,)
