# Imports
import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Connection, create_engine


# Global variables
engine = create_engine(os.environ["DATABASE_URL"])


# Code
def get_conn() -> Iterator[Connection]:
    """
    One connection per request, in a transaction that commits at the end
    and rolls back when the request raises
    """

    with engine.begin() as conn:
        yield conn


@contextmanager
def transaction() -> Iterator[Connection]:
    """
    One connection from the pool, in a transaction that commits at the end
    of the block and rolls back when it raises
    """

    with engine.begin() as conn:
        yield conn
