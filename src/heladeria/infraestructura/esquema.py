"""Saltos de esquema B04. La apertura de la base controla la transacción completa."""

from enum import StrEnum
from sqlite3 import Connection
from uuid import UUID


def crear_catalogo(con: Connection) -> None:
    con.execute("""
        CREATE TABLE schema_migration (
            version INTEGER PRIMARY KEY CHECK (version > 0),
            applied_at TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE config_revision (
            id TEXT PRIMARY KEY NOT NULL,
            parent_id TEXT REFERENCES config_revision(id),
            created_at TEXT NOT NULL, source TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE app_state (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            dataset_id TEXT NOT NULL, mode TEXT NOT NULL CHECK (mode IN ('REAL', 'DEMO')),
            created_at TEXT NOT NULL,
            config_head_id TEXT REFERENCES config_revision(id),
            schedule_head_id TEXT CHECK (schedule_head_id IS NULL),
            input_epoch INTEGER NOT NULL DEFAULT 0 CHECK (input_epoch >= 0)
        )
    """)
    con.execute("""
        CREATE TRIGGER proteger_conjunto BEFORE UPDATE OF dataset_id, mode ON app_state
        BEGIN
            SELECT RAISE(ABORT, 'La identidad y el modo del conjunto son inmutables');
        END
    """)
    con.execute("CREATE TABLE person (person_id TEXT PRIMARY KEY NOT NULL)")
    con.execute("""
        CREATE TABLE config_item_version (
            id TEXT PRIMARY KEY NOT NULL,
            item_id TEXT NOT NULL, kind TEXT NOT NULL CHECK (kind IN ('PERSON', 'OFF_QUOTA', 'MINUTES_TARGET')),
            scope_id TEXT NOT NULL REFERENCES person(person_id),
            from_date TEXT NOT NULL, until_date TEXT CHECK (from_date < until_date),
            rule_version INTEGER NOT NULL CHECK (rule_version > 0),
            payload_version INTEGER NOT NULL CHECK (payload_version = 1),
            payload_json TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE config_member (
            config_revision_id TEXT NOT NULL REFERENCES config_revision(id),
            item_version_id TEXT NOT NULL REFERENCES config_item_version(id),
            PRIMARY KEY (config_revision_id, item_version_id)
        )
    """)
    con.execute("CREATE INDEX config_scope ON config_item_version (scope_id, kind, item_id, from_date)")


def crear_asignaciones(con: Connection) -> None:
    con.execute("""
        CREATE TABLE day_assignment (
            id TEXT PRIMARY KEY NOT NULL, person_id TEXT NOT NULL REFERENCES person(person_id),
            op_date TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ('WORK','FIXED_OFF','ROTATING_OFF','ABSENCE','UNASSIGNED')),
            display_label TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('EMPLOYEE','OWNER')),
            UNIQUE (id, person_id, op_date)
        )
    """)
    con.execute("CREATE INDEX assignment_person_date ON day_assignment (person_id, op_date)")
    con.execute("""
        CREATE TABLE work_block (
            assignment_id TEXT NOT NULL REFERENCES day_assignment(id),
            ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
            start_min INTEGER NOT NULL, end_min INTEGER NOT NULL CHECK (end_min > start_min),
            start_offset_min INTEGER NOT NULL, end_offset_min INTEGER NOT NULL,
            PRIMARY KEY (assignment_id, ordinal)
        )
    """)
    con.execute("CREATE INDEX block_time ON work_block (start_min, end_min)")


MIGRACIONES = (crear_catalogo, crear_asignaciones)


ID_APLICACION = 0x48484C41  # HHLA, identificador del formato en la cabecera SQLite.


class Modo(StrEnum):
    REAL = "REAL"
    DEMO = "DEMO"


class ErrorBase(RuntimeError):
    """El almacén no se pudo abrir con las garantías requeridas."""


def verificar_base(conexion: Connection, modo: Modo, version: int) -> None:
    """Comprueba el archivo activo o su copia dentro de una lectura consistente."""
    if not 1 <= version <= len(MIGRACIONES):
        raise ErrorBase(f"Versión de esquema no soportada: {version}.")
    if conexion.execute("PRAGMA application_id").fetchone()[0] != ID_APLICACION:
        raise ErrorBase("El archivo SQLite pertenece a otra aplicación.")
    if conexion.execute("PRAGMA user_version").fetchone()[0] != version:
        raise ErrorBase("La versión del archivo no coincide con la esperada.")
    if conexion.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ErrorBase("Falló la verificación de integridad de SQLite.")
    if conexion.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ErrorBase("Hay referencias huérfanas en la base.")

    historial = conexion.execute("SELECT version FROM schema_migration ORDER BY version")
    if [fila[0] for fila in historial] != list(range(1, version + 1)):
        raise ErrorBase("El historial de migraciones difiere de la versión de la base.")
    estados = conexion.execute(
        "SELECT singleton, dataset_id, mode, input_epoch FROM app_state"
    ).fetchall()
    if len(estados) != 1 or estados[0][0] != 1 or estados[0][2] != modo.value:
        raise ErrorBase(f"La identidad o el modo del almacén difiere del esperado ({modo.value}).")
    try:
        UUID(estados[0][1])
    except (ValueError, TypeError, AttributeError) as exc:
        raise ErrorBase("El identificador del conjunto de datos es inválido.") from exc

    # Estas lecturas comprueban las relaciones que los repositorios deben poder abrir.
    conexion.execute(
        "SELECT p.person_id, v.item_id, v.kind, v.scope_id, v.from_date, v.until_date, "
        "v.rule_version, v.payload_version, v.payload_json, r.parent_id, r.created_at, r.source "
        "FROM person p "
        "JOIN config_item_version v ON v.scope_id = p.person_id "
        "JOIN config_member m ON m.item_version_id = v.id "
        "JOIN config_revision r ON r.id = m.config_revision_id LIMIT 1"
    ).fetchone()
    if version >= 2:
        conexion.execute(
            "SELECT a.person_id, a.op_date, a.state, a.display_label, a.role, b.ordinal, "
            "b.start_min, b.end_min, b.start_offset_min, b.end_offset_min "
            "FROM day_assignment a LEFT JOIN work_block b ON b.assignment_id = a.id LIMIT 1"
        ).fetchone()
