import os
from collections.abc import Iterator

from sqlalchemy import Connection, create_engine


engine = create_engine(os.environ["DATABASE_URL"])


def get_conn() -> Iterator[Connection]:
    with engine.begin() as conn:
        yield conn
