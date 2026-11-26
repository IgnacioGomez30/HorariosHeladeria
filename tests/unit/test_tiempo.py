from datetime import date, datetime, time, timedelta, timezone

import pytest

from heladeria.dominio.tiempo import (
    Agenda, Intervalo, Jornada, descanso, dia_civil, fecha_hora_local, minuto_local,
)


LUNES = date(2026, 11, 30)
MARTES = LUNES + timedelta(days=1)
MIERCOLES = MARTES + timedelta(days=1)


def bloque(dia, inicio, fin, mas_dias=0):
    return Intervalo(minuto_local(dia, time.fromisoformat(inicio)),
                     minuto_local(dia + timedelta(days=mas_dias), time.fromisoformat(fin)))


def test_T02_nocturnas_y_17_horas_de_descanso():
    lunes = Jornada("A", LUNES, (bloque(LUNES, "19:00", "01:00", 1),))
    martes = Jornada("A", MARTES, (bloque(MARTES, "18:00", "00:00", 1),))
    agenda = Agenda((martes, lunes))
    assert [lunes.minutos, martes.minutos] == [360, 360]
    assert agenda.minutos_operativos("A", LUNES, MIERCOLES) == 720
    assert agenda.minutos_de_presencia("A", dia_civil(MARTES)) == 420
    assert descanso(lunes, martes) == 17 * 60
    assert fecha_hora_local(lunes.fin).date() == MARTES
    assert fecha_hora_local(martes.fin).date() == MIERCOLES


def test_T01_presencias_semiabiertas_y_oraculo_por_minuto():
    a = Jornada("A", LUNES, (bloque(LUNES, "12:00", "16:00"),))
    b = Jornada("B", LUNES, (bloque(LUNES, "15:00", "21:00"),))
    dia = dia_civil(LUNES)
    for agenda in (Agenda((a, b)), Agenda((b, a))):
        for t in range(1440):
            esperado = set()
            if 720 <= t < 960:
                esperado.add("A")
            if 900 <= t < 1260:
                esperado.add("B")
            assert agenda.presentes(dia.inicio + t) == esperado


def test_T03_pausa_partida():
    jornada = Jornada("A", LUNES, (bloque(LUNES, "20:00", "00:00", 1),
                                   bloque(LUNES, "12:00", "16:00")))
    assert jornada.minutos == 480
    agenda = Agenda((jornada,))
    assert agenda.minutos_de_presencia("A", bloque(LUNES, "16:00", "20:00")) == 0
    assert agenda.presentes(minuto_local(LUNES, time(20))) == {"A"}


def test_T04_solape_de_un_minuto_y_adyacencia():
    base = bloque(LUNES, "12:00", "16:00")
    with pytest.raises(ValueError, match="A"):
        Jornada("A", LUNES, (base, bloque(LUNES, "15:59", "18:00")))
    contigua = Jornada("A", LUNES, (base, bloque(LUNES, "16:00", "18:00")))
    continua = Jornada("A", LUNES, (bloque(LUNES, "12:00", "18:00"),))
    assert contigua.minutos == continua.minutos == 360
    assert Agenda((contigua,)).presentes(base.fin) == {"A"}


@pytest.mark.parametrize("inicio", [date(2027, 1, 31), date(2026, 12, 31),
                                     date(2028, 12, 31)])
def test_T05_bordes_de_semana_mes_y_anio(inicio):
    fin = inicio + timedelta(days=1)
    agenda = Agenda((Jornada("A", inicio, (bloque(inicio, "19:00", "01:00", 1),)),))
    assert agenda.minutos_operativos("A", inicio, fin) == 360
    assert agenda.minutos_operativos("A", fin, fin + timedelta(days=1)) == 0
    assert agenda.minutos_de_presencia("A", dia_civil(fin)) == 60


@pytest.mark.parametrize("inicio,fin", [("00:50", "01:10"), ("01:15", "01:45")])
def test_rechaza_solape_y_jornada_intercalada_en_una_pausa(inicio, fin):
    partida = Jornada("A", LUNES, (bloque(LUNES, "22:00", "01:00", 1),
                                   bloque(MARTES, "02:00", "03:00")))
    otra = Jornada("A", MARTES, (bloque(MARTES, inicio, fin),))
    with pytest.raises(ValueError, match="A"):
        Agenda((partida, otra))


def test_dos_jornadas_para_la_misma_casilla():
    a = Jornada("A", LUNES, (Intervalo(10, 20),))
    b = Jornada("A", LUNES, (Intervalo(20, 30),))
    with pytest.raises(ValueError, match="A"):
        Agenda((a, b))
    with pytest.raises(ValueError):
        Jornada("A", LUNES, ())


def test_T27_minutos_fuera_de_grilla_exactos():
    tramo = bloque(LUNES, "12:07", "13:03")
    assert tramo.minutos == 56
    assert tramo.contiene(minuto_local(LUNES, time(12, 11)))
    assert fecha_hora_local(tramo.inicio).isoformat() == "2026-11-30T12:07:00-03:00"
    with pytest.raises(ValueError):
        bloque(LUNES, "12:07", "12:07")


@pytest.mark.parametrize("hora", [time(17, 7, 1), time(17, 7, 0, 1),
                                  time(17, 7, tzinfo=timezone.utc)])
def test_rechaza_hora_ajena_a_reloj_civil_de_minutos(hora):
    with pytest.raises(ValueError):
        minuto_local(LUNES, hora)


def test_dst_mendoza_hora_inexistente_y_ambigua():
    with pytest.raises(ValueError, match="inexistente"):
        minuto_local(date(2007, 12, 30), time(0, 30))
    dia = date(2008, 3, 15)
    with pytest.raises(ValueError, match="ambigua"):
        minuto_local(dia, time(23, 30))
    primero = minuto_local(dia, time(23, 30), ocurrencia=0)
    segundo = minuto_local(dia, time(23, 30), ocurrencia=1)
    assert segundo - primero == 60
    assert dia_civil(dia).minutos == 25 * 60


def test_el_epoch_es_utc_y_los_bloques_son_minutos_enteros():
    assert minuto_local(date(1970, 1, 1), time(9)) == 12 * 60
    for valor in (12.5, False):
        with pytest.raises((TypeError, ValueError)):
            Intervalo(valor, 20)
    with pytest.raises((TypeError, ValueError)):
        Jornada("A", datetime(2027, 1, 1), (Intervalo(0, 1),))


def test_dia_civil_empieza_en_el_primer_minuto_existente():
    domingo = date(2007, 12, 30)
    dia = dia_civil(domingo)
    assert dia.minutos == 23 * 60
    assert fecha_hora_local(dia.inicio).isoformat() == "2007-12-30T01:00:00-02:00"
    assert dia_civil(domingo - timedelta(days=1)).fin == dia.inicio
    assert fecha_hora_local(dia.fin).isoformat() == "2007-12-31T00:00:00-02:00"
