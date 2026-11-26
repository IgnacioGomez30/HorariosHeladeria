"""Casos sintéticos de cupos operativos y disponibilidad física (Mendoza)."""
from datetime import date, time, timedelta

import pytest

from heladeria.dominio.disponibilidad import Disponibilidad, FranjaSemanal, Indisponibilidad
from heladeria.dominio.francos import (
    Casilla, CupoFrancos, EstadoCasilla, cupo_de_semana, evaluar_semana, racha_maxima,
)
from heladeria.dominio.patrones import HoraLocal
from heladeria.dominio.personas import Persona, Rol
from heladeria.dominio.reglas import DatoPendiente, Regla, Vigencia
from heladeria.dominio.tiempo import Intervalo, Jornada, minuto_local


LUNES = date(2027, 2, 1)
MARTES = LUNES + timedelta(days=1)
DIA = timedelta(days=1)
FIJO = EstadoCasilla.FRANCO_FIJO
ROTATIVO = EstadoCasilla.FRANCO_ROTATIVO


def trabajo(persona, fecha):
    bloque = Intervalo(minuto_local(fecha, time(12)), minuto_local(fecha, time(15)))
    return Casilla(persona, fecha, EstadoCasilla.TRABAJO, Jornada(persona, fecha, (bloque,)))


def semana(persona, estados):
    casillas = []
    for indice in range(7):
        fecha = LUNES + indice * DIA
        casilla = (Casilla(persona, fecha, estados[indice])
                   if indice in estados else trabajo(persona, fecha))
        casillas.append(casilla)
    return casillas


def test_T06_fijo_y_rotativo_exigen_dos_fechas_por_persona():
    cupo_a = CupoFrancos(frozenset({1}), 1)
    cupo_b = CupoFrancos(frozenset(), 1)
    casillas = semana("A", {1: FIJO, 5: ROTATIVO}) + semana("B", {0: ROTATIVO})
    a = evaluar_semana("A", LUNES, casillas, cupo_a)
    assert a.cumple
    assert a.fechas_fijas == {MARTES}
    assert a.fechas_rotativas == {date(2027, 2, 6)}
    assert evaluar_semana("B", LUNES, casillas, cupo_b).cumple


@pytest.mark.parametrize("estados", [
    {1: FIJO}, {1: ROTATIVO}, {0: FIJO, 5: ROTATIVO},
    {1: FIJO, 5: EstadoCasilla.AUSENCIA}, {1: FIJO, 5: EstadoCasilla.SIN_ASIGNAR},
    {1: FIJO, 5: ROTATIVO, 6: ROTATIVO},
])
def test_T06_T30_cumplimiento_exacto_con_origen_del_franco(estados):
    assert not evaluar_semana("A", LUNES, semana("A", estados), CupoFrancos({1}, 1)).cumple


def test_T26_una_ventana_parcial_requiere_el_resto_de_la_semana():
    casillas = semana("A", {1: FIJO, 5: ROTATIVO})
    with pytest.raises(DatoPendiente, match="2027-02-07"):
        evaluar_semana("A", LUNES, casillas[:-1], CupoFrancos({1}, 1))


def test_T06_dos_casillas_para_la_misma_fecha_no_dan_doble_credito():
    casillas = semana("A", {1: FIJO})
    casillas.append(Casilla("A", MARTES, ROTATIVO))
    with pytest.raises(ValueError, match="2027-02-02"):
        evaluar_semana("A", LUNES, casillas, CupoFrancos({1}, 1))


def test_T30_integridad_entre_estado_e_identidad_de_la_jornada():
    jornada = trabajo("B", MARTES).jornada
    for args in [
        ("A", MARTES, EstadoCasilla.TRABAJO, None),
        ("A", MARTES, EstadoCasilla.TRABAJO, jornada),
        ("B", LUNES, EstadoCasilla.TRABAJO, jornada),
        ("B", MARTES, FIJO, jornada),
    ]:
        with pytest.raises(ValueError):
            Casilla(*args)


def test_T09_cambio_de_cupo_en_el_ciclo_exige_regla_transitoria_explicita():
    clave = "francos:A"
    viejas = CupoFrancos({1}, 1)
    nuevas = CupoFrancos(set(), 2)
    reglas = (
        Regla(clave, 1, Vigencia(LUNES, MARTES), viejas),
        Regla(clave, 2, Vigencia(MARTES), nuevas),
    )
    with pytest.raises(DatoPendiente, match="transitori"):
        cupo_de_semana(reglas, clave, LUNES)
    transitoria = Regla(clave, 3, Vigencia(LUNES, LUNES + 7 * DIA), viejas)
    assert cupo_de_semana(reglas, clave, LUNES, transitoria) == viejas
    assert cupo_de_semana(reglas, clave, LUNES + 7 * DIA) == nuevas
    with pytest.raises(ValueError):
        cupo_de_semana(reglas, clave, LUNES + 7 * DIA, transitoria)


def test_T14_racha_de_doce_fechas_cruza_el_lunes_y_preserva_contexto():
    lunes = date(2026, 11, 2)
    fechas = [lunes + i * DIA for i in range(14)]
    casillas = [Casilla("A", fechas[0], ROTATIVO)]
    casillas += [trabajo("A", fecha) for fecha in fechas[1:-1]]
    casillas.append(Casilla("A", fechas[-1], FIJO))
    empleada = Persona("Demo A", Rol.EMPLEADO, lunes, id="A")
    assert racha_maxima(empleada, fechas[0], fechas[-1] + DIA, casillas) == 12
    with pytest.raises(DatoPendiente):
        racha_maxima(empleada, fechas[0], fechas[-1] + DIA, casillas[7:])


def test_T07_la_indisponibilidad_civil_incluye_cola_del_lunes_y_termina_a_medianoche():
    inicio = minuto_local(MARTES, time(0))
    fin = minuto_local(MARTES + DIA, time(0))
    jornada = Jornada("A", LUNES, (Intervalo(inicio - 300, inicio + 60),))
    siguiente = Jornada("A", MARTES + DIA, (Intervalo(fin, fin + 30),))
    otra = Jornada("B", LUNES, jornada.bloques)
    franco_operativo = Casilla("A", MARTES, FIJO)
    assert franco_operativo.jornada is None
    restriccion = Indisponibilidad.dia_completo("A", MARTES)
    assert restriccion.conflictos([otra, jornada, siguiente]) == (Intervalo(inicio, inicio + 60),)


def test_T04_ultimo_minuto_fuera_de_la_union_de_ventanas_es_incompatible():
    inicio = minuto_local(LUNES, time(12))
    fin = minuto_local(LUNES, time(18))
    jornada = Jornada("A", LUNES, (Intervalo(inicio, fin),))
    permitidos = (Intervalo(inicio, inicio + 120), Intervalo(inicio + 120, fin - 1))
    disponibilidad = Disponibilidad("A", permitidos)
    assert disponibilidad.conflictos(jornada) == (Intervalo(fin - 1, fin),)


def test_T30_bloques_partidos_pueden_evitar_una_indisponibilidad_parcial():
    inicio = minuto_local(LUNES, time(12))
    ventana = Intervalo(inicio, inicio + 360)
    pausa = Intervalo(inicio + 120, inicio + 240)
    jornada = Jornada("A", LUNES, (Intervalo(inicio, pausa.inicio), Intervalo(pausa.fin, ventana.fin)))
    disponibilidad = Disponibilidad("A", (ventana,), (pausa,))
    assert disponibilidad.conflictos(jornada) == ()
    assert disponibilidad.conflictos(Jornada("A", LUNES, (ventana,))) == (pausa,)


def test_disponibilidad_recurrente_usa_vigencia_y_dias_explicitos():
    franja = FranjaSemanal(0, HoraLocal(time(19, 7)), HoraLocal(time(1), 1),
                          Vigencia(LUNES, LUNES + 7 * DIA))
    assert franja.materializar(LUNES) == Intervalo(
        minuto_local(LUNES, time(19, 7)), minuto_local(MARTES, time(1))
    )
    assert franja.materializar(MARTES) is None
    assert franja.materializar(LUNES + 7 * DIA) is None


def test_T30_sin_asignar_admite_un_propietario_sin_compromiso():
    casilla = Casilla("J", LUNES, EstadoCasilla.SIN_ASIGNAR)
    propietario = Persona("Demo J", Rol.PROPIETARIO, LUNES, id="J")
    assert racha_maxima(propietario, LUNES, MARTES, [casilla]) == 0
    empleado = Persona("Demo A", Rol.EMPLEADO, LUNES, id="A")
    with pytest.raises(DatoPendiente):
        racha_maxima(empleado, LUNES, MARTES, [Casilla("A", LUNES, EstadoCasilla.SIN_ASIGNAR)])


def test_transicion_semanal_sin_cupo_explicito_queda_pendiente():
    transicion = Regla("cupo:A", 1, Vigencia(LUNES, LUNES + 7 * DIA), None)
    with pytest.raises(DatoPendiente, match="cupo:A"):
        cupo_de_semana((), "cupo:A", LUNES, transicion)
