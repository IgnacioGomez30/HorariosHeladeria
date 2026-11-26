"""Calendario efectivo del local y materialización de una variante autorizada."""

from collections.abc import Collection, Iterable
from dataclasses import dataclass
from datetime import date, time, timedelta
from enum import Enum

from .personas import Persona
from .reglas import DatoPendiente, Regla, ReglaAmbigua
from .tiempo import Intervalo, Jornada, minuto_local


@dataclass(frozen=True)
class HoraLocal:
    hora: time
    dias: int = 0
    ocurrencia: int | None = None

    def __post_init__(self):
        if type(self.dias) is not int:
            raise ValueError("El desplazamiento de fecha debe darse en días enteros.")
        if self.hora.tzinfo is not None or self.hora.second or self.hora.microsecond:
            raise ValueError("Indique una hora local con precisión de minuto.")

    def resolver(self, fecha_operativa: date) -> int:
        dia = fecha_operativa + timedelta(days=self.dias)
        return minuto_local(dia, self.hora, ocurrencia=self.ocurrencia)


@dataclass(frozen=True)
class Horario:
    """Un atributo omitido puede heredarse de otra regla de menor prioridad."""

    apertura: HoraLocal | None = None
    cierre: HoraLocal | None = None
    cerrado: bool = False

    def __post_init__(self):
        tiene_horas = self.apertura is not None or self.cierre is not None
        if self.cerrado == tiene_horas:
            raise ValueError("Indique horas de atención o el estado cerrado.")


class Especial(Enum):
    FERIADO = "feriado"
    VISPERA = "víspera"


@dataclass(frozen=True)
class ReglaCalendario:
    horario: Regla[Horario | None]
    selector: int | Especial | date  # 0 = lunes, o especial o fecha concreta.
    prioridad: int = 0

    def __post_init__(self):
        if type(self.selector) is int:
            if self.selector not in range(7):
                raise ValueError("El día de semana debe estar entre 0 y 6.")
        elif type(self.selector) is not date and not isinstance(self.selector, Especial):
            raise ValueError("Selector de calendario desconocido.")
        if type(self.prioridad) is not int:
            raise ValueError("La prioridad debe ser entera.")
        if self.prioridad and not isinstance(self.selector, Especial):
            raise ValueError("Solo las reglas especiales admiten prioridad explícita.")

    def precedencia(self, dia: date, feriados: Collection[date]) -> tuple[int, int] | None:
        if not self.horario.vigencia.contiene(dia):
            return None
        if self.selector == dia:
            return 2, 0
        if self.selector is Especial.FERIADO and dia in feriados:
            return 1, self.prioridad
        if self.selector is Especial.VISPERA and dia + timedelta(days=1) in feriados:
            return 1, self.prioridad
        if self.selector == dia.weekday():
            return 0, 0
        return None


@dataclass(frozen=True)
class DiaLocal:
    fecha: date
    publico: Intervalo | None  # None representa un cierre explícito.
    fuentes: tuple[tuple[str, int], ...]


def _extremo_efectivo(
    atributo: str, dia: date, aplicables: list[tuple[tuple[int, int], Regla[Horario | None]]],
) -> tuple[int | None, set[tuple[str, int]]]:
    # Cerrado participa como valor explícito para ambos extremos.
    candidatos = [
        (nivel, regla) for nivel, regla in aplicables
        if regla.valor is None or regla.valor.cerrado or getattr(regla.valor, atributo) is not None
    ]
    if not candidatos:
        raise DatoPendiente(f"Falta {atributo} del local para {dia}.")
    nivel_efectivo = max(nivel for nivel, _ in candidatos)
    fuentes = set()
    minutos = set()
    for nivel, regla in candidatos:
        if nivel != nivel_efectivo:
            continue
        if regla.valor is None:
            raise DatoPendiente(f"Falta {atributo} de {regla.clave} v{regla.version} para {dia}.")
        fuentes.add(regla.fuente)
        extremo = getattr(regla.valor, atributo)
        minutos.add(None if extremo is None else extremo.resolver(dia))
    if len(minutos) != 1:
        raise ReglaAmbigua(f"{atributo} de {dia} incompatible entre {sorted(fuentes)}.")
    return minutos.pop(), fuentes


def resolver_dia(
    dia: date, reglas: Iterable[ReglaCalendario], feriados: Collection[date],
) -> DiaLocal:
    """Proyecta horarios públicos usando el calendario de feriados provisto offline."""
    aplicables = []
    for regla in reglas:
        nivel = regla.precedencia(dia, feriados)
        if nivel is not None:
            aplicables.append((nivel, regla.horario))
    apertura, origen_apertura = _extremo_efectivo("apertura", dia, aplicables)
    cierre, origen_cierre = _extremo_efectivo("cierre", dia, aplicables)
    fuentes = tuple(sorted(origen_apertura | origen_cierre))
    if apertura is None and cierre is None:
        return DiaLocal(dia, None, fuentes)
    if apertura is None or cierre is None:
        raise DatoPendiente(f"Falta completar el horario de reapertura del {dia}.")
    return DiaLocal(dia, Intervalo(apertura, cierre), fuentes)


class Ancla(Enum):
    APERTURA = "apertura"
    CIERRE = "cierre"


@dataclass(frozen=True)
class Relativo:
    ancla: Ancla
    minutos: int

    def __post_init__(self):
        if not isinstance(self.ancla, Ancla) or type(self.minutos) is not int:
            raise ValueError("La referencia requiere apertura o cierre y un desplazamiento entero.")


@dataclass(frozen=True)
class BloquePatron:
    inicio: HoraLocal | Relativo
    fin: HoraLocal | Relativo


@dataclass(frozen=True)
class Patron:
    """Una variante completa. La ventana desplaza juntos todos sus bloques."""

    personas: frozenset[str]
    dias: frozenset[int]
    bloques: tuple[BloquePatron, ...]
    desplazamiento_min: int = 0
    desplazamiento_max: int = 0

    def __post_init__(self):
        object.__setattr__(self, "personas", frozenset(self.personas))
        object.__setattr__(self, "dias", frozenset(self.dias))
        object.__setattr__(self, "bloques", tuple(self.bloques))
        if not self.personas or not self.dias or not self.bloques:
            raise ValueError("El patrón requiere personas, días aplicables y al menos un bloque.")
        if any(type(dia) is not int or dia not in range(7) for dia in self.dias):
            raise ValueError("El día de semana debe estar entre 0 y 6.")
        if any(type(v) is not int for v in (self.desplazamiento_min, self.desplazamiento_max)):
            raise ValueError("La ventana del patrón se expresa en minutos enteros.")
        if self.desplazamiento_max < self.desplazamiento_min:
            raise ValueError("La ventana del patrón está invertida.")


def _materializar_extremo(extremo: HoraLocal | Relativo, fecha: date, dia: DiaLocal | None) -> int:
    if isinstance(extremo, HoraLocal):
        return extremo.resolver(fecha)
    if dia is None or dia.publico is None:
        raise DatoPendiente(f"Falta el ancla de {extremo.ancla.value} para {fecha}.")
    base = dia.publico.inicio if extremo.ancla is Ancla.APERTURA else dia.publico.fin
    return base + extremo.minutos


def materializar(
    regla: Regla[Patron], persona: Persona, fecha: date, dia: DiaLocal | None = None,
    *, desplazamiento: int = 0,
) -> Jornada:
    """Materializa una elección manual exacta de la versión seleccionada."""
    if dia is not None and dia.fecha != fecha:
        raise ValueError("La fecha del calendario difiere de la fecha operativa.")
    if not regla.vigencia.contiene(fecha):
        raise ValueError(f"Patrón {regla.clave} fuera de vigencia en {fecha}.")
    patron = regla.valor
    if persona.id not in patron.personas or fecha.weekday() not in patron.dias:
        raise ValueError(f"Patrón {regla.clave} sin autorización para {persona.id} en {fecha}.")
    if type(desplazamiento) is not int or not patron.desplazamiento_min <= desplazamiento <= patron.desplazamiento_max:
        raise ValueError(f"Desplazamiento fuera de la ventana de {regla.clave}.")
    bloques = tuple(
        Intervalo(
            _materializar_extremo(b.inicio, fecha, dia) + desplazamiento,
            _materializar_extremo(b.fin, fecha, dia) + desplazamiento,
        )
        for b in patron.bloques
    )
    return persona.jornada(fecha, bloques)
