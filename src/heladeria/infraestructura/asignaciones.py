"""Persistencia de valores materializados que podrán referenciar distintas revisiones."""

import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from uuid import uuid4

from heladeria.dominio.francos import Casilla, EstadoCasilla
from heladeria.dominio.personas import Rol
from heladeria.dominio.tiempo import Intervalo, Jornada, fecha_hora_local

from .repositorios import persona_por_id
from .transacciones import escritura


@dataclass(frozen=True)
class AsignacionGuardada:
    casilla: Casilla
    etiqueta_visible: str
    rol: Rol
    desfases: tuple[tuple[int, int], ...]


def _desfase(instante: int) -> int:
    # Coincide con la precisión del esquema incluso para reglas IANA históricas.
    desplazamiento = fecha_hora_local(instante).utcoffset()
    minutos, resto = divmod(desplazamiento, timedelta(minutes=1))
    if resto:
        raise ValueError("El desfase histórico no se puede representar en minutos")
    return minutos


def guardar_asignacion(con: sqlite3.Connection, casilla: Casilla) -> str:
    """Agrega una casilla inmutable y sus bloques en la misma transacción."""
    identificador = str(uuid4())
    with escritura(con):
        persona = persona_por_id(con, casilla.persona_id)
        if persona is None:
            raise ValueError(f"Falta la ficha de la persona {casilla.persona_id}")
        if not persona.activa(casilla.fecha_operativa):
            raise ValueError(f"{persona.id} está fuera de actividad el {casilla.fecha_operativa}")
        con.execute(
            """INSERT INTO day_assignment (id, person_id, op_date, state, display_label, role)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (identificador, persona.id, casilla.fecha_operativa.isoformat(), casilla.estado.value,
             persona.distintivo, persona.rol.value),
        )
        if casilla.jornada:
            con.executemany(
                """INSERT INTO work_block
                       (assignment_id, ordinal, start_min, end_min, start_offset_min, end_offset_min)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ((identificador, ordinal, b.inicio, b.fin, _desfase(b.inicio), _desfase(b.fin))
                 for ordinal, b in enumerate(casilla.jornada.bloques)),
            )
    return identificador


def asignacion_por_id(con: sqlite3.Connection, identificador: str) -> AsignacionGuardada | None:
    """Lee el estado y la presentación histórica con los bloques en su orden original."""
    fila = con.execute(
        """SELECT person_id, op_date, state, display_label, role
           FROM day_assignment WHERE id = ?""",
        (identificador,),
    ).fetchone()
    if fila is None:
        return None

    persona_id, fecha_iso, estado, etiqueta, rol = fila
    fecha = date.fromisoformat(fecha_iso)
    bloques = []
    desfases = []
    for inicio, fin, desfase_inicio, desfase_fin in con.execute(
        """SELECT start_min, end_min, start_offset_min, end_offset_min FROM work_block
           WHERE assignment_id = ? ORDER BY ordinal""",
        (identificador,),
    ):
        bloques.append(Intervalo(inicio, fin))
        desfases.append((desfase_inicio, desfase_fin))
    jornada = Jornada(persona_id, fecha, tuple(bloques)) if bloques else None
    casilla = Casilla(persona_id, fecha, EstadoCasilla(estado), jornada)
    return AsignacionGuardada(casilla, etiqueta, Rol(rol), tuple(desfases))
