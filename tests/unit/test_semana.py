"""Demostración F1. Todas las personas, jornadas y cuotas son ficticias."""

from datetime import date, time, timedelta

from heladeria.dominio.francos import (
    Casilla,
    CupoFrancos,
    EstadoCasilla,
    evaluar_semana,
)
from heladeria.dominio.tiempo import (
    Agenda,
    Intervalo,
    Jornada,
    descanso,
    dia_civil,
    minuto_local,
)


def bloque(fecha, inicio, fin, dias_hasta_fin=0):
    return Intervalo(
        minuto_local(fecha, time.fromisoformat(inicio)),
        minuto_local(fecha + timedelta(days=dias_hasta_fin), time.fromisoformat(fin)),
    )


def test_T01_T07_T28_semana_en_memoria_con_ambos_vecinos():
    lunes = date(2027, 2, 1)
    dia = timedelta(days=1)
    martes, miercoles, jueves, viernes, sabado, domingo = (
        lunes + n * dia for n in range(1, 7)
    )

    # A cierra el lunes tras una pausa libre. B hace dos jornadas nocturnas.
    jornadas = [
        Jornada(
            "A", lunes,
            (bloque(lunes, "12:00", "16:00"), bloque(lunes, "20:00", "01:00", 1)),
        ),
        Jornada("A", domingo, (bloque(domingo, "19:00", "01:00", 1),)),
        Jornada("B", lunes, (bloque(lunes, "19:00", "01:00", 1),)),
        Jornada("B", martes, (bloque(martes, "18:00", "00:00", 1),)),
    ]
    for persona, fechas in (
        ("A", (miercoles, viernes, sabado)),
        ("B", (miercoles, jueves, viernes, sabado)),
    ):
        for fecha in fechas:
            jornadas.append(Jornada(persona, fecha, (bloque(fecha, "12:00", "16:00"),)))

    casillas = [
        Casilla(j.persona_id, j.fecha_operativa, EstadoCasilla.TRABAJO, j)
        for j in jornadas
    ]
    casillas.extend((
        Casilla("A", martes, EstadoCasilla.FRANCO_FIJO),
        Casilla("A", jueves, EstadoCasilla.FRANCO_ROTATIVO),
        Casilla("B", domingo, EstadoCasilla.FRANCO_ROTATIVO),
    ))
    for persona, fijos, rotativos in (("A", {martes}, {jueves}), ("B", set(), {domingo})):
        cupo = CupoFrancos(frozenset(f.weekday() for f in fijos), len(rotativos))
        balance = evaluar_semana(persona, lunes, casillas, cupo)
        assert balance.cumple
        assert balance.fechas_fijas == fijos
        assert balance.fechas_rotativas == rotativos

    previo, siguiente = lunes - dia, domingo + dia
    cierre_previo = Jornada("A", previo, (bloque(previo, "19:00", "01:00", 1),))
    apertura_siguiente = Jornada("A", siguiente, (bloque(siguiente, "12:00", "16:00"),))
    agenda = Agenda((cierre_previo, *jornadas, apertura_siguiente))

    assert agenda.minutos_operativos("A", lunes, siguiente) == 540 + 3 * 240 + 360
    assert agenda.minutos_operativos("B", lunes, siguiente) == 360 + 360 + 4 * 240
    assert agenda.minutos_de_presencia("A", dia_civil(lunes)) == 60 + 240 + 240
    assert agenda.minutos_de_presencia("A", dia_civil(martes)) == 60
    assert agenda.minutos_de_presencia("B", dia_civil(martes)) == 60 + 360
    assert agenda.presentes(minuto_local(martes, time(0, 59))) == {"A", "B"}
    assert agenda.presentes(minuto_local(martes, time(1))) == set()
    assert agenda.presentes(minuto_local(lunes, time(18))) == set()
    assert agenda.minutos_de_presencia("A", dia_civil(siguiente)) == 60 + 240

    por_clave = {(j.persona_id, j.fecha_operativa): j for j in jornadas}
    assert descanso(cierre_previo, por_clave["A", lunes]) == 11 * 60
    assert descanso(por_clave["B", lunes], por_clave["B", martes]) == 17 * 60
    assert descanso(por_clave["A", domingo], apertura_siguiente) == 11 * 60


def test_T05_T27_trasladar_un_dia_conserva_duracion_y_presencia():
    # En estas fechas el desfase de Mendoza permanece constante.
    fechas = (date(2026, 12, 31), date(2027, 1, 1))
    resultados = []
    for fecha in fechas:
        jornada = Jornada("A", fecha, (bloque(fecha, "23:37", "00:19", 1),))
        agenda = Agenda((jornada,))
        manana = fecha + timedelta(days=1)
        resultados.append((
            agenda.minutos_operativos("A", fecha, manana),
            agenda.minutos_de_presencia("A", dia_civil(fecha)),
            agenda.minutos_de_presencia("A", dia_civil(manana)),
        ))
    assert resultados == [(42, 23, 19), (42, 23, 19)]
