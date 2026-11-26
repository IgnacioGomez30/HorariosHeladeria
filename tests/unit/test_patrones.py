from dataclasses import replace
from datetime import date, time, timedelta
from itertools import product

import pytest

from heladeria.dominio.patrones import (
    Ancla, BloquePatron, Especial, HoraLocal, Horario, Patron, ReglaCalendario,
    Relativo, materializar, resolver_dia,
)
from heladeria.dominio.personas import Persona, Rol
from heladeria.dominio.reglas import (
    ClaseRegla, DatoPendiente, MetaMinutos, Regla, ReglaAmbigua, Vigencia, resolver_regla,
)
from heladeria.dominio.tiempo import Intervalo, minuto_local

LUNES = date(2027, 2, 1)
MARTES = LUNES + timedelta(days=1)
VIGENTE = Vigencia(LUNES)
SEMANA = frozenset(range(7))
DEMO_A = Persona("Demo A", Rol.EMPLEADO, LUNES, id="A")
DEMO_B = Persona("Demo B", Rol.EMPLEADO, LUNES, id="B")


def hora(hora, minuto=0, dia=0):
    return HoraLocal(time(hora, minuto), dia)


def patron(fin, dias=SEMANA):
    return Patron(frozenset({"A"}), dias, (BloquePatron(hora(12), hora(fin)),))


def calendario(clave, selector, horario, prioridad=0):
    return ReglaCalendario(Regla(clave, 1, VIGENTE, horario), selector, prioridad)


def test_T08_variantes_personales_y_objetivos():
    reglas = (
        Regla("corta", 1, VIGENTE, patron(15)),
        Regla("larga", 1, VIGENTE, patron(18)),
    )
    duraciones = [
        [materializar(resolver_regla(reglas, clave, dia), DEMO_A, dia).minutos
         for clave in ("corta", "larga")]
        for dia in (LUNES, MARTES)
    ]
    combinaciones = list(product(*duraciones))
    exacta = MetaMinutos(540, ClaseRegla.OBLIGATORIA)
    preferida = MetaMinutos(500, ClaseRegla.PREFERENCIA)
    imposible = MetaMinutos(500, ClaseRegla.OBLIGATORIA)
    assert [c for c in combinaciones if exacta.admite(sum(c))] == [(180, 360), (360, 180)]
    assert all(preferida.admite(sum(c)) for c in combinaciones)
    assert min(preferida.desvio(sum(c)) for c in combinaciones) == 40
    assert not any(imposible.admite(sum(c)) for c in combinaciones)
    with pytest.raises(ValueError, match="corta.*A"):
        materializar(Regla("corta", 2, VIGENTE, patron(15, frozenset({0}))), DEMO_A, MARTES)
    with pytest.raises(ValueError, match="corta.*B"):
        materializar(reglas[0], DEMO_B, LUNES)


def test_T09_versiones_adyacentes_y_ambiguedad():
    d14 = date(2027, 2, 14)
    d15 = d14 + timedelta(days=1)
    primera = Regla("base", 1, Vigencia(LUNES, d15), patron(18))
    segunda = Regla("base", 2, Vigencia(d15), patron(19))
    reglas = (segunda, primera)
    assert materializar(resolver_regla(reglas, "base", d14), DEMO_A, d14).minutos == 360
    assert materializar(resolver_regla(reglas, "base", d15), DEMO_A, d15).minutos == 420
    with pytest.raises(DatoPendiente, match="base.*2027-01-31"):
        resolver_regla(reglas, "base", LUNES - timedelta(days=1))
    with pytest.raises(DatoPendiente, match="pendiente"):
        resolver_regla((Regla("base", 1, VIGENTE, None),), "base", d14)
    with pytest.raises(ReglaAmbigua, match="base.*1.*3"):
        resolver_regla((*reglas, Regla("base", 3, VIGENTE, patron(17))), "base", d14)
    with pytest.raises(ValueError, match="vigencia"):
        materializar(primera, DEMO_A, d15)


def test_T10_feriado_y_vispera_coincidentes_se_resuelven_por_atributo():
    feriados = {LUNES, MARTES}
    normal = calendario("habitual", 0, Horario(hora(12), hora(20)))
    feriado = calendario("feriado", Especial.FERIADO, Horario(hora(12), hora(21)))
    vispera = calendario("vispera", Especial.VISPERA, Horario(cierre=hora(22)))
    base = (normal, feriado, vispera)
    with pytest.raises(ReglaAmbigua, match="feriado.*vispera"):
        resolver_dia(LUNES, base, feriados)
    excepcional = calendario("excepcion", LUNES, Horario(hora(13), hora(18)))
    efectivo = resolver_dia(LUNES, (*base, excepcional), feriados)
    assert efectivo.publico == Intervalo(minuto_local(LUNES, time(13)), minuto_local(LUNES, time(18)))
    assert efectivo.fuentes == (("excepcion", 1),)
    cierre = calendario("solo_cierre", LUNES, Horario(cierre=hora(0, dia=1)))
    efectivo = resolver_dia(LUNES, (*base, cierre), feriados)
    medianoche = minuto_local(MARTES, time(0))
    assert efectivo.publico.inicio == minuto_local(LUNES, time(12))
    assert efectivo.publico.fin == medianoche
    assert not efectivo.publico.contiene(medianoche)
    assert efectivo.fuentes == (("feriado", 1), ("solo_cierre", 1))
    prioritaria = calendario("vispera", Especial.VISPERA, Horario(cierre=hora(22)), 1)
    assert resolver_dia(LUNES, (normal, feriado, prioritaria), feriados).publico.fin == minuto_local(LUNES, time(22))


def test_cerrado_desconocido_y_ancla_faltante():
    with pytest.raises(DatoPendiente, match="2027-02-01"):
        resolver_dia(LUNES, (), set())
    regla = Regla("preparacion", 1, VIGENTE, Patron(
        frozenset({"A"}), SEMANA,
        (BloquePatron(Relativo(Ancla.APERTURA, -20), Relativo(Ancla.CIERRE, 10)),),
    ))
    cerrado = calendario("cerrado", LUNES, Horario(cerrado=True))
    dia = resolver_dia(LUNES, (cerrado,), set())
    assert dia.publico is None
    with pytest.raises(DatoPendiente, match="apertura"):
        materializar(regla, DEMO_A, LUNES, dia)
    with pytest.raises(DatoPendiente, match="apertura"):
        materializar(regla, DEMO_A, LUNES)
    abierto = calendario("lunes", 0, Horario(hora(12), hora(0, dia=1)))
    dia = resolver_dia(LUNES, (abierto,), set())
    jornada = materializar(regla, DEMO_A, LUNES, dia)
    assert jornada.inicio == minuto_local(LUNES, time(11, 40))
    assert jornada.fin == minuto_local(MARTES, time(0, 10))
    with pytest.raises(ValueError, match="fecha"):
        materializar(regla, DEMO_A, MARTES, dia)


def test_patron_partido_con_ventana_admite_minuto_exacto():
    regla = Regla("partido", 1, VIGENTE, Patron(
        frozenset({"A"}), SEMANA,
        (BloquePatron(hora(17), hora(19)), BloquePatron(hora(0, dia=1), hora(1, dia=1))),
        desplazamiento_min=0, desplazamiento_max=15,
    ))
    jornada = materializar(regla, DEMO_A, LUNES, desplazamiento=7)
    assert jornada.bloques == (
        Intervalo(minuto_local(LUNES, time(17, 7)), minuto_local(LUNES, time(19, 7))),
        Intervalo(minuto_local(MARTES, time(0, 7)), minuto_local(MARTES, time(1, 7))),
    )
    assert jornada.minutos == 180
    with pytest.raises(ValueError, match="ventana"):
        materializar(regla, DEMO_A, LUNES, desplazamiento=16)


def test_dominio_rechaza_configuracion_inconsistente():
    with pytest.raises(ValueError):
        Vigencia(MARTES, LUNES)
    with pytest.raises(ValueError):
        Regla("", 1, VIGENTE, "ejemplo")
    with pytest.raises(ValueError):
        Patron(frozenset({"A"}), frozenset({7}), (BloquePatron(hora(12), hora(16)),))
    with pytest.raises(ValueError):
        Horario(cerrado=True, apertura=hora(12))


def test_T21_el_patron_respeta_la_baja_de_la_persona():
    regla = Regla("base", 1, VIGENTE, patron(18))
    persona = replace(DEMO_A, hasta=MARTES)
    assert materializar(regla, persona, LUNES).minutos == 360
    with pytest.raises(ValueError, match="actividad"):
        materializar(regla, persona, MARTES)


def test_T10_dato_pendiente_solo_si_es_aplicable_al_horario_efectivo():
    semanal = calendario("habitual", 0, Horario(hora(12), hora(20)))
    especial = calendario("feriado", Especial.FERIADO, None)
    with pytest.raises(DatoPendiente, match="feriado"):
        resolver_dia(LUNES, (semanal, especial), {LUNES})
    excepcion = calendario("fecha", LUNES, Horario(hora(13), hora(18)))
    assert resolver_dia(LUNES, (semanal, especial, excepcion), {LUNES}).fuentes == (("fecha", 1),)
