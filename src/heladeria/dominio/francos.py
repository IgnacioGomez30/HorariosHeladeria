"""Casillas efectivas y cupos de una semana operativa, de lunes a domingo."""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from .personas import Persona, Rol
from .reglas import DatoPendiente, Regla, resolver_regla
from .tiempo import Jornada


class EstadoCasilla(StrEnum):
    TRABAJO = "WORK"
    FRANCO_FIJO = "FIXED_OFF"
    FRANCO_ROTATIVO = "ROTATING_OFF"
    AUSENCIA = "ABSENCE"
    SIN_ASIGNAR = "UNASSIGNED"


@dataclass(frozen=True)
class Casilla:
    persona_id: str
    fecha_operativa: date
    estado: EstadoCasilla
    jornada: Jornada | None = None

    def __post_init__(self):
        if not isinstance(self.persona_id, str) or not self.persona_id.strip():
            raise ValueError("La casilla requiere un ID de persona")
        if type(self.fecha_operativa) is not date:
            raise ValueError("La casilla requiere una fecha operativa")
        object.__setattr__(self, "estado", EstadoCasilla(self.estado))
        if (self.estado == EstadoCasilla.TRABAJO) != (self.jornada is not None):
            raise ValueError("Únicamente una casilla de trabajo debe contener una jornada")
        if self.jornada is not None and (
            self.persona_id != self.jornada.persona_id
            or self.fecha_operativa != self.jornada.fecha_operativa
        ):
            raise ValueError("La persona y la fecha de la jornada deben coincidir con la casilla")


@dataclass(frozen=True)
class CupoFrancos:
    """Días fijos (lunes=0) y cantidad exacta de rotativos adicionales del ciclo."""
    dias_fijos: frozenset[int]
    rotativos: int

    def __post_init__(self):
        dias = frozenset(self.dias_fijos)
        if any(type(dia) is not int or not 0 <= dia < 7 for dia in dias):
            raise ValueError("Los días fijos deben estar entre 0 (lunes) y 6 (domingo)")
        if type(self.rotativos) is not int or not 0 <= self.rotativos <= 7 - len(dias):
            raise ValueError("Los cupos deben caber en siete fechas diferentes")
        object.__setattr__(self, "dias_fijos", dias)


def _fin_semana(lunes: date) -> date:
    if lunes.weekday() != 0:
        raise ValueError("Indicar el lunes de la semana operativa")
    return lunes + timedelta(days=7)


def cupo_de_semana(
    reglas: Iterable[Regla[CupoFrancos]],
    clave: str,
    lunes: date,
    transicion: Regla[CupoFrancos] | None = None,
) -> CupoFrancos:
    """Una transición aprobada contiene el cupo específico de este ciclo completo."""
    fin = _fin_semana(lunes)
    if transicion is not None:
        if (transicion.clave != clave or transicion.vigencia.desde != lunes
                or transicion.vigencia.hasta != fin):
            raise ValueError("La regla transitoria debe corresponder a la clave y semana exactas")
        return resolver_regla((transicion,), clave, lunes).valor
    reglas = tuple(reglas)
    cupo = resolver_regla(reglas, clave, lunes).valor
    for dias in range(1, 7):
        siguiente = resolver_regla(reglas, clave, lunes + timedelta(days=dias))
        if siguiente.valor != cupo:
            raise DatoPendiente(f"{clave}: falta un cupo transitorio para la semana del {lunes}")
    return cupo


def _casillas_en_orden(
    persona_id: str, desde: date, hasta: date, casillas: Iterable[Casilla]
) -> list[Casilla]:
    """Exige una casilla conocida por fecha del contexto [desde, hasta)."""
    if hasta <= desde:
        raise ValueError("El período debe contener al menos un día")
    por_fecha = {}
    for casilla in casillas:
        if casilla.persona_id == persona_id and desde <= casilla.fecha_operativa < hasta:
            if casilla.fecha_operativa in por_fecha:
                raise ValueError(f"{persona_id}: casilla duplicada el {casilla.fecha_operativa}")
            por_fecha[casilla.fecha_operativa] = casilla
    ordenadas = []
    for indice in range((hasta - desde).days):
        fecha = desde + timedelta(days=indice)
        if fecha not in por_fecha:
            raise DatoPendiente(f"{persona_id}: falta la casilla del {fecha}")
        ordenadas.append(por_fecha[fecha])
    return ordenadas


@dataclass(frozen=True)
class BalanceFrancos:
    fechas_fijas: frozenset[date]
    fechas_rotativas: frozenset[date]
    cupo: CupoFrancos

    @property
    def cumple(self) -> bool:
        dias_fijos = {fecha.weekday() for fecha in self.fechas_fijas}
        return dias_fijos == self.cupo.dias_fijos and len(self.fechas_rotativas) == self.cupo.rotativos


def evaluar_semana(
    persona_id: str, lunes: date, casillas: Iterable[Casilla], cupo: CupoFrancos
) -> BalanceFrancos:
    """Compara únicamente francos con el cupo explícito aplicable a esa persona y ciclo."""
    semana = _casillas_en_orden(persona_id, lunes, _fin_semana(lunes), casillas)
    return BalanceFrancos(
        frozenset(c.fecha_operativa for c in semana if c.estado == EstadoCasilla.FRANCO_FIJO),
        frozenset(c.fecha_operativa for c in semana if c.estado == EstadoCasilla.FRANCO_ROTATIVO),
        cupo,
    )


def racha_maxima(persona: Persona, desde: date, hasta: date, casillas: Iterable[Casilla]) -> int:
    """Máximo de fechas operativas trabajadas seguidas en el contexto [desde, hasta)."""
    actual = maxima = 0
    for casilla in _casillas_en_orden(persona.id, desde, hasta, casillas):
        if casilla.estado == EstadoCasilla.TRABAJO:
            actual += 1
            maxima = max(actual, maxima)
        elif casilla.estado == EstadoCasilla.SIN_ASIGNAR and persona.rol is Rol.EMPLEADO:
            raise DatoPendiente(f"{persona.id}: sin asignación el {casilla.fecha_operativa}")
        else:
            actual = 0
    return maxima
