"""Casillas materializadas de demo que atraviesan el cierre de la conexión."""

import sqlite3
from dataclasses import replace
from datetime import date, time

import pytest

from heladeria.dominio.francos import Casilla, EstadoCasilla
from heladeria.dominio.personas import Persona, Rol
from heladeria.dominio.tiempo import Intervalo, minuto_local
from heladeria.infraestructura.asignaciones import asignacion_por_id, guardar_asignacion
from heladeria.infraestructura.base import Modo, abrir_base
from heladeria.infraestructura.repositorios import guardar_persona


FECHA = date(2007, 12, 29)
SIGUIENTE = date(2007, 12, 30)


def partida(persona):
    bloques = (
        Intervalo(minuto_local(FECHA, time(12)), minuto_local(FECHA, time(16))),
        Intervalo(minuto_local(FECHA, time(22)), minuto_local(SIGUIENTE, time(2))),
    )
    return Casilla(persona.id, FECHA, EstadoCasilla.TRABAJO, persona.jornada(FECHA, bloques))


def test_T03_T21_reabre_partida_con_ficha_y_desfases_historicos(tmp_path):
    persona = Persona("Demo Sol", Rol.EMPLEADO, FECHA, etiqueta="Prueba")
    inicial = partida(persona)
    with abrir_base(tmp_path, Modo.DEMO) as con:
        guardar_persona(con, persona)
        trabajo_id = guardar_asignacion(con, inicial)
        libres = {}
        for estado in EstadoCasilla:
            if estado != EstadoCasilla.TRABAJO:
                casilla = Casilla(persona.id, SIGUIENTE, estado)
                libres[guardar_asignacion(con, casilla)] = casilla
        guardar_persona(con, replace(persona, nombre="Demo Luna", rol=Rol.PROPIETARIO))

    with abrir_base(tmp_path, Modo.DEMO) as con:
        registro = asignacion_por_id(con, trabajo_id)
        assert registro.casilla == inicial
        assert registro.casilla.jornada.minutos == 420
        assert registro.rol == Rol.EMPLEADO
        assert registro.etiqueta_visible == persona.distintivo
        assert registro.desfases == ((-180, -180), (-180, -120))
        for identificador, esperado in libres.items():
            registro = asignacion_por_id(con, identificador)
            assert registro.casilla == esperado
            assert registro.desfases == ()
        assert asignacion_por_id(con, "inexistente") is None


def test_error_en_segundo_bloque_revierte_asignacion_completa(tmp_path):
    persona = Persona("Demo Sol", Rol.EMPLEADO, FECHA)
    with abrir_base(tmp_path, Modo.DEMO) as con:
        guardar_persona(con, persona)
        con.execute("""CREATE TEMP TRIGGER fallo BEFORE INSERT ON work_block
                       WHEN NEW.ordinal = 1 BEGIN SELECT RAISE(ABORT, 'fallo de prueba'); END""")
        with pytest.raises(sqlite3.IntegrityError, match="fallo de prueba"):
            guardar_asignacion(con, partida(persona))
    with abrir_base(tmp_path, Modo.DEMO) as con:
        assert con.execute("SELECT count(*) FROM day_assignment").fetchone()[0] == 0
        assert con.execute("SELECT count(*) FROM work_block").fetchone()[0] == 0
