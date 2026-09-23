from contextlib import contextmanager
from typing import Any, Iterator

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from common.config import settings


pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10,
    kwargs={"row_factory": dict_row},
    open=False,
)


def open_pool() -> None:
    if pool.closed:
        pool.open(wait=True)


def close_pool() -> None:
    if not pool.closed:
        pool.close()


@contextmanager
def transaction() -> Iterator[Any]:
    open_pool()
    with pool.connection() as conn:
        with conn.transaction():
            yield conn


def query_all(sql: str, params: tuple | list = ()) -> list[dict]:
    with transaction() as conn:
        return list(conn.execute(sql, params).fetchall())


def query_one(sql: str, params: tuple | list = ()) -> dict | None:
    with transaction() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql: str, params: tuple | list = ()) -> int:
    with transaction() as conn:
        cur = conn.execute(sql, params)
        return cur.rowcount
