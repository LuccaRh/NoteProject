# Imports
import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Connection, create_engine


# Global variables
engine = create_engine(os.environ["NUJABES_DATABASE_URL"])


# Code
@contextmanager
def transaction() -> Iterator[Connection]:
    """
    One connection from the pool, in a transaction that commits at the end
    of the block and rolls back when it raises
    """

    with engine.begin() as conn:
        yield conn
