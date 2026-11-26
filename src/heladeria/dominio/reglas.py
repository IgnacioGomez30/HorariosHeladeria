"""Identidad y resolución de versiones para una clave de política sustituible."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import Enum


class DatoPendiente(ValueError):
    """La información disponible no determina el valor solicitado."""


class ReglaAmbigua(DatoPendiente):
    """Hay fuentes incompatibles con igual precedencia."""


@dataclass(frozen=True)
class Vigencia:
    desde: date
    hasta: date | None = None  # Extremo exclusivo.

    def __post_init__(self):
        if type(self.desde) is not date or self.hasta is not None and type(self.hasta) is not date:
            raise ValueError("La vigencia requiere fechas operativas.")
        if self.hasta is not None and self.hasta <= self.desde:
            raise ValueError("La vigencia debe tener duración positiva.")

    def contiene(self, fecha: date) -> bool:
        return self.desde <= fecha and (self.hasta is None or fecha < self.hasta)


@dataclass(frozen=True)
class Regla[T]:
    """Una clave identifica una sola familia, alcance y unidad configurados."""

    clave: str
    version: int
    vigencia: Vigencia
    valor: T

    def __post_init__(self):
        if not self.clave.strip() or type(self.version) is not int or self.version < 1:
            raise ValueError("Cada regla requiere clave y versión positiva.")

    @property
    def fuente(self) -> tuple[str, int]:
        return self.clave, self.version


def resolver_regla[T](reglas: Iterable[Regla[T]], clave: str, fecha: date) -> Regla[T]:
    vigentes = sorted(
        (r for r in reglas if r.clave == clave and r.vigencia.contiene(fecha)),
        key=lambda r: r.version,
    )
    if not vigentes:
        raise DatoPendiente(f"Falta la regla {clave} para {fecha}.")
    ultima = vigentes[-1]
    if any(r.valor != ultima.valor for r in vigentes):
        versiones = ", ".join(str(r.version) for r in vigentes)
        raise ReglaAmbigua(f"Regla {clave} en {fecha}: versiones incompatibles {versiones}.")
    if ultima.valor is None:
        raise DatoPendiente(f"La regla {clave} v{ultima.version} está pendiente para {fecha}.")
    return ultima


class ClaseRegla(Enum):
    OBLIGATORIA = "obligatoria"
    PREFERENCIA = "preferencia"


@dataclass(frozen=True)
class MetaMinutos:
    """Objetivo para el total imputado al período que indique la regla fuente."""

    minutos: int
    clase: ClaseRegla

    def __post_init__(self):
        if type(self.minutos) is not int or self.minutos < 0:
            raise ValueError("La meta debe darse en minutos enteros no negativos.")
        if not isinstance(self.clase, ClaseRegla):
            raise ValueError("Indique el carácter obligatorio o preferente de la meta.")

    def desvio(self, total_operativo: int) -> int:
        if type(total_operativo) is not int or total_operativo < 0:
            raise ValueError("El total debe darse en minutos enteros no negativos.")
        return abs(total_operativo - self.minutos)

    def admite(self, total_operativo: int) -> bool:
        desvio = self.desvio(total_operativo)
        return desvio == 0 or self.clase is ClaseRegla.PREFERENCIA
