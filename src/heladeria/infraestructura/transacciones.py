"""Atomicidad de las escrituras del repositorio, también bajo un caso de uso externo."""

from collections.abc import Iterator
from contextlib import contextmanager
from sqlite3 import Connection


@contextmanager
def escritura(con: Connection) -> Iterator[None]:
    anidada = con.in_transaction
    con.execute("SAVEPOINT repositorio" if anidada else "BEGIN IMMEDIATE")
    try:
        yield
        con.execute("RELEASE repositorio" if anidada else "COMMIT")
    except BaseException:
        if con.in_transaction:
            if anidada:
                con.execute("ROLLBACK TO repositorio")
                con.execute("RELEASE repositorio")
            else:
                con.execute("ROLLBACK")
        raise
