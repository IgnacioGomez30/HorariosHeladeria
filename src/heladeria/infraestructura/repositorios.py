"""Catálogo de personas y líneas de reglas por revisión de configuración."""

import json
from collections.abc import Iterable
from datetime import UTC, date, datetime
from itertools import pairwise
from sqlite3 import Connection
from uuid import uuid4

from heladeria.dominio.francos import CupoFrancos
from heladeria.dominio.personas import Persona, Rol, catalogo_personal
from heladeria.dominio.reglas import ClaseRegla, MetaMinutos, Regla, Vigencia

from .transacciones import escritura


type ValorRegla = CupoFrancos | MetaMinutos | None


def _cabeza(con: Connection) -> str | None:
    return con.execute("SELECT config_head_id FROM app_state WHERE singleton = 1").fetchone()[0]


def _nueva_revision(con: Connection, persona_id: str, clave: str, ficha: bool) -> str:
    """Hereda toda la revisión salvo la ficha o línea que se está reemplazando."""
    padre = _cabeza(con)
    revision = str(uuid4())
    con.execute(
        "INSERT INTO config_revision(id, parent_id, created_at, source) VALUES(?,?,?,?)",
        (revision, padre, datetime.now(UTC).isoformat(), "MANUAL"),
    )
    con.execute(
        """INSERT INTO config_member(config_revision_id, item_version_id)
           SELECT ?, v.id FROM config_member m
           JOIN config_item_version v ON v.id = m.item_version_id
           WHERE m.config_revision_id = ?
             AND NOT (v.scope_id = ? AND v.item_id = ? AND (v.kind = 'PERSON') = ?)""",
        (revision, padre, persona_id, clave, ficha),
    )
    con.execute("UPDATE app_state SET config_head_id = ?, input_epoch = input_epoch + 1 "
                "WHERE singleton = 1", (revision,))
    return revision


def _agregar_version(con: Connection, revision: str, persona_id: str, clave: str,
                     tipo: str, numero: int, vigencia: Vigencia, contenido: dict | None) -> None:
    version_id = str(uuid4())
    con.execute(
        """INSERT INTO config_item_version
           (id, item_id, kind, scope_id, from_date, until_date, rule_version, payload_version, payload_json)
           VALUES(?, ?, ?, ?, ?, ?, ?, 1, ?)""",
        (version_id, clave, tipo, persona_id, vigencia.desde.isoformat(),
         vigencia.hasta.isoformat() if vigencia.hasta else None, numero, json.dumps(contenido)),
    )
    con.execute("INSERT INTO config_member VALUES (?, ?)", (revision, version_id))


def _leer_ficha(persona_id: str, desde: str, hasta: str | None, datos: str) -> Persona:
    payload = json.loads(datos)
    return Persona(payload["nombre"], Rol(payload["rol"]), date.fromisoformat(desde),
                   date.fromisoformat(hasta) if hasta else None, payload["etiqueta"], persona_id)


_FICHAS = """
    SELECT v.scope_id, v.from_date, v.until_date, v.payload_json
    FROM config_member m JOIN config_item_version v ON v.id = m.item_version_id
    WHERE m.config_revision_id = ? AND v.kind = 'PERSON'
"""


def persona_por_id(con: Connection, persona_id: str, revision: str | None = None) -> Persona | None:
    if revision is None:
        revision = _cabeza(con)
    fila = con.execute(_FICHAS + " AND v.scope_id = ?", (revision, persona_id)).fetchone()
    return _leer_ficha(*fila) if fila else None


def guardar_persona(con: Connection, persona: Persona) -> str:
    with escritura(con):
        cabeza = _cabeza(con)
        if cabeza and persona_por_id(con, persona.id, cabeza) == persona:
            return cabeza
        otras = con.execute(_FICHAS + " AND v.scope_id <> ?", (cabeza, persona.id))
        catalogo_personal([persona, *(_leer_ficha(*fila) for fila in otras)])
        con.execute("INSERT INTO person(person_id) VALUES (?) ON CONFLICT(person_id) DO NOTHING",
                    (persona.id,))
        numero = con.execute(
            """SELECT coalesce(max(rule_version), 0) + 1 FROM config_item_version
               WHERE kind = 'PERSON' AND scope_id = ?""", (persona.id,)
        ).fetchone()[0]
        revision = _nueva_revision(con, persona.id, persona.id, ficha=True)
        _agregar_version(con, revision, persona.id, persona.id, "PERSON", numero,
                         Vigencia(persona.desde, persona.hasta),
                         {"nombre": persona.nombre, "rol": persona.rol.value, "etiqueta": persona.etiqueta})
        return revision


_REGLAS = """
    FROM config_member m JOIN config_item_version v ON v.id = m.item_version_id
    WHERE m.config_revision_id = ? AND v.scope_id = ? AND v.item_id = ? AND v.kind <> 'PERSON'
"""


def reglas_de_persona(con: Connection, persona_id: str, clave: str,
                      revision: str | None = None) -> tuple[Regla[ValorRegla], ...]:
    if revision is None:
        revision = _cabeza(con)
    filas = con.execute(
        "SELECT v.kind, v.rule_version, v.from_date, v.until_date, v.payload_json " +
        _REGLAS + " ORDER BY v.from_date", (revision, persona_id, clave)
    )
    reglas = []
    for tipo, numero, desde, hasta, datos in filas:
        payload = json.loads(datos)
        vigencia = Vigencia(date.fromisoformat(desde), date.fromisoformat(hasta) if hasta else None)
        valor = None
        if payload is not None:
            if tipo == "OFF_QUOTA":
                valor = CupoFrancos(payload["dias_fijos"], payload["rotativos"])
            elif tipo == "MINUTES_TARGET":
                valor = MetaMinutos(payload["minutos"], ClaseRegla(payload["clase"]))
            else:
                raise ValueError(f"Familia de regla desconocida: {tipo}")
        reglas.append(Regla(clave, numero, vigencia, valor))
    return tuple(reglas)


def guardar_reglas(con: Connection, persona_id: str, reglas: Iterable[Regla[ValorRegla]]) -> str:
    """Reemplaza la línea temporal completa de una clave personal en una nueva revisión."""
    linea = tuple(sorted(reglas, key=lambda regla: regla.vigencia.desde))
    if not linea:
        raise ValueError("La línea de reglas necesita una clave y al menos una versión.")
    clave = linea[0].clave
    if any(r.clave != clave for r in linea) or len({r.version for r in linea}) != len(linea):
        raise ValueError("Se requiere una clave con versiones distintas.")
    for anterior, siguiente in pairwise(linea):
        if anterior.vigencia.hasta is None or siguiente.vigencia.desde < anterior.vigencia.hasta:
            raise ValueError("Las vigencias de la misma línea se superponen.")

    with escritura(con):
        cabeza = _cabeza(con)
        if persona_por_id(con, persona_id, cabeza) is None:
            raise ValueError("Falta la ficha de la persona a la que se aplica la regla.")
        if reglas_de_persona(con, persona_id, clave, cabeza) == linea:
            return cabeza
        previa = con.execute("SELECT DISTINCT v.kind " + _REGLAS, (cabeza, persona_id, clave)).fetchall()
        familias = {fila[0] for fila in previa}
        contenidos = []
        for regla in linea:
            match regla.valor:
                case CupoFrancos(dias_fijos=dias, rotativos=cantidad):
                    familias.add("OFF_QUOTA")
                    contenidos.append({"dias_fijos": sorted(dias), "rotativos": cantidad})
                case MetaMinutos(minutos=minutos, clase=clase):
                    familias.add("MINUTES_TARGET")
                    contenidos.append({"minutos": minutos, "clase": clase.value})
                case None:
                    contenidos.append(None)
                case _:
                    raise ValueError("Tipo de regla no admitido por este esquema.")
        if len(familias) != 1:
            raise ValueError("La línea debe identificar una sola familia de reglas.")
        tipo = familias.pop()
        revision = _nueva_revision(con, persona_id, clave, ficha=False)
        for regla, contenido in zip(linea, contenidos, strict=True):
            _agregar_version(con, revision, persona_id, clave, tipo, regla.version,
                             regla.vigencia, contenido)
        return revision
