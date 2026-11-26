"""Ventanas físicas autorizadas y excepciones de indisponibilidad confirmadas."""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from .patrones import HoraLocal
from .reglas import Vigencia
from .tiempo import Intervalo, Jornada, dia_civil


@dataclass(frozen=True)
class FranjaSemanal:
    """Ventana recurrente. Se materializa en la zona del local al resolver una fecha."""
    dia_semana: int
    inicio: HoraLocal
    fin: HoraLocal
    vigencia: Vigencia

    def __post_init__(self):
        if type(self.dia_semana) is not int or not 0 <= self.dia_semana <= 6:
            raise ValueError("El día semanal debe estar entre lunes (0) y domingo (6)")

    def materializar(self, fecha: date) -> Intervalo | None:
        if fecha.weekday() != self.dia_semana or not self.vigencia.contiene(fecha):
            return None
        return Intervalo(self.inicio.resolver(fecha), self.fin.resolver(fecha))


def _unir(intervalos: Iterable[Intervalo]) -> tuple[Intervalo, ...]:
    unidos = []
    for actual in sorted(intervalos, key=lambda intervalo: intervalo.inicio):
        if unidos and actual.inicio <= unidos[-1].fin:
            previo = unidos[-1]
            unidos[-1] = Intervalo(previo.inicio, max(previo.fin, actual.fin))
        else:
            unidos.append(actual)
    return tuple(unidos)


@dataclass(frozen=True)
class Indisponibilidad:
    persona_id: str
    intervalo: Intervalo

    @classmethod
    def dia_completo(cls, persona_id: str, fecha: date) -> 'Indisponibilidad':
        return cls(persona_id, dia_civil(fecha))

    def conflictos(self, jornadas: Iterable[Jornada]) -> tuple[Intervalo, ...]:
        """Incluye las jornadas vecinas provistas, cualquiera sea su fecha operativa."""
        conflictos = []
        for jornada in jornadas:
            if jornada.persona_id == self.persona_id:
                for bloque in jornada.bloques:
                    cruce = self.intervalo.interseccion(bloque)
                    if cruce is not None:
                        conflictos.append(cruce)
        return _unir(conflictos)


@dataclass(frozen=True)
class Disponibilidad:
    """Disponibilidad efectiva de una persona ya materializada para el horizonte.

    Los permisos se unen y los impedimentos confirmados prevalecen. Una colección
    vacía de permisos declara cero disponibilidad en el horizonte consultado.
    """
    persona_id: str
    permitidos: tuple[Intervalo, ...]
    impedimentos: tuple[Intervalo, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "permitidos", _unir(self.permitidos))
        object.__setattr__(self, "impedimentos", _unir(self.impedimentos))

    def conflictos(self, jornada: Jornada) -> tuple[Intervalo, ...]:
        """Devuelve solo los tramos efectivamente trabajados fuera de disponibilidad."""
        if jornada.persona_id != self.persona_id:
            raise ValueError("La disponibilidad y la jornada deben corresponder a la misma persona")
        conflictos = []
        for bloque in jornada.bloques:
            cursor = bloque.inicio
            for permitido in self.permitidos:
                cruce = permitido.interseccion(bloque)
                if cruce is None:
                    continue
                if cursor < cruce.inicio:
                    conflictos.append(Intervalo(cursor, cruce.inicio))
                cursor = cruce.fin
            if cursor < bloque.fin:
                conflictos.append(Intervalo(cursor, bloque.fin))
            for impedimento in self.impedimentos:
                cruce = impedimento.interseccion(bloque)
                if cruce is not None:
                    conflictos.append(cruce)
        return _unir(conflictos)
