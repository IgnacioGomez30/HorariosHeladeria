"""Ficha inmutable, identidad estable y participación en el mínimo de presencia."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import uuid4

from .tiempo import Agenda, Intervalo, Jornada


class Rol(StrEnum):
    EMPLEADO = "EMPLOYEE"
    PROPIETARIO = "OWNER"


@dataclass(frozen=True)
class Persona:
    nombre: str
    rol: Rol
    desde: date
    hasta: date | None = None
    etiqueta: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if not self.id.strip() or not self.nombre.strip():
            raise ValueError("Se requiere ID estable y nombre visible.")
        if not isinstance(self.rol, Rol):
            raise ValueError("Rol de persona desconocido.")
        if type(self.desde) is not date or (self.hasta is not None and type(self.hasta) is not date):
            raise ValueError("La actividad requiere fechas operativas.")
        if self.hasta is not None and self.hasta <= self.desde:
            raise ValueError("El fin exclusivo debe ser posterior al alta.")

    @property
    def distintivo(self) -> str:
        rol = "empleado" if self.rol == Rol.EMPLEADO else "propietario"
        partes = (self.nombre, rol, self.etiqueta)
        return " · ".join(parte for parte in partes if parte)

    def activa(self, fecha: date) -> bool:
        return self.desde <= fecha and (self.hasta is None or fecha < self.hasta)

    def jornada(self, fecha: date, bloques: tuple[Intervalo, ...]) -> Jornada:
        if not self.activa(fecha):
            raise ValueError(f"{self.id} está fuera de actividad el {fecha}.")
        return Jornada(self.id, fecha, bloques)


def catalogo_personal(fichas: Iterable[Persona]) -> dict[str, Persona]:
    """Indexa una versión de ficha por identidad y exige rótulos distinguibles."""
    por_id = {}
    etiquetas = {}
    for ficha in fichas:
        if ficha.id in por_id:
            raise ValueError(f"Identidad repetida en el catálogo: {ficha.id}.")
        grupo = (ficha.nombre.strip().casefold(), ficha.rol)
        usadas = etiquetas.setdefault(grupo, set())
        etiqueta = ficha.etiqueta.strip().casefold()
        if usadas and (not etiqueta or "" in usadas or etiqueta in usadas):
            raise ValueError("Indicar una etiqueta distinta para cada homónimo del mismo rol.")
        usadas.add(etiqueta)
        por_id[ficha.id] = ficha
    return por_id


def presentes_para_minimo(
    agenda: Agenda, instante: int, personal: Mapping[str, Persona],
    compromisos: Mapping[str, Sequence[Intervalo]],
) -> frozenset[str]:
    """Recibe solo los compromisos aprobados; un propietario eventual aporta cero."""
    elegibles = set()
    for clave in agenda.presentes(instante):
        persona = personal.get(clave)
        if persona is None or persona.id != clave:
            raise ValueError(f"Falta ficha para la persona asignada {clave}.")
        if persona.rol == Rol.EMPLEADO or any(c.contiene(instante) for c in compromisos.get(clave, ())):
            elegibles.add(clave)
    return frozenset(elegibles)
