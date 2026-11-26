from dataclasses import replace
from datetime import date

import pytest

from heladeria.dominio.personas import Persona, Rol, catalogo_personal, presentes_para_minimo
from heladeria.dominio.tiempo import Agenda, Intervalo


LUNES = date(2027, 2, 1)
MARTES = date(2027, 2, 2)


def test_T21_homonimos_baja_e_identidad_estable():
    persona = Persona("Demo Sol", Rol.EMPLEADO, LUNES)
    otra = Persona("Demo Sol", Rol.PROPIETARIO, LUNES)
    assert persona.id != otra.id
    assert persona.distintivo != otra.distintivo
    baja = replace(persona, hasta=MARTES)
    assert baja.id == persona.id
    assert baja.jornada(LUNES, (Intervalo(0, 1),)).persona_id == persona.id
    with pytest.raises(ValueError, match="actividad"):
        baja.jornada(MARTES, (Intervalo(0, 1),))


def test_T11_apoyo_solo_en_la_interseccion_comprometida_y_asignada():
    a = Persona("Demo A", Rol.EMPLEADO, LUNES)
    j = Persona("Demo J", Rol.PROPIETARIO, LUNES)
    tramo = Intervalo(0, 20)
    agenda = Agenda((a.jornada(LUNES, (tramo,)), j.jornada(LUNES, (tramo,))))
    personal = {p.id: p for p in (a, j)}
    compromisos = {j.id: (Intervalo(10, 25),)}
    assert presentes_para_minimo(agenda, 0, personal, compromisos) == {a.id}
    assert presentes_para_minimo(agenda, 10, personal, compromisos) == {a.id, j.id}
    assert presentes_para_minimo(agenda, 20, personal, compromisos) == set()


def test_catalogo_exige_etiquetas_para_homonimos_del_mismo_rol():
    a = Persona("Demo Sol", Rol.EMPLEADO, LUNES)
    b = Persona("Demo Sol", Rol.EMPLEADO, LUNES)
    with pytest.raises(ValueError, match="etiqueta"):
        catalogo_personal([a, b])
    norte = replace(a, etiqueta="Norte")
    sur = replace(b, etiqueta="Sur")
    assert catalogo_personal([norte, sur]) == {norte.id: norte, sur.id: sur}
    with pytest.raises(ValueError, match="etiqueta"):
        catalogo_personal([norte, replace(sur, etiqueta="norte")])
    with pytest.raises(ValueError, match="repetid"):
        catalogo_personal([a, a])
