# Imports
import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Connection, create_engine, text

from ichiro.user import current_user


# Global variables
engine = create_engine(os.environ["ICHIRO_DATABASE_URL"])


# Code
def set_user(conn: Connection) -> None:
    """
    Tells Postgres the user of the request until the transaction ends:
    the notes policy shows and takes only the rows of app.user_id (empty
    without a user, so no rows)
    """

    user_id = current_user.get()
    conn.execute(
        text("SELECT set_config('app.user_id', :user_id, true)"),
        {"user_id": "" if user_id is None else str(user_id)},
    )


@contextmanager
def transaction() -> Iterator[Connection]:
    """
    One connection from the pool, in a transaction of the request's user
    that commits at the end of the block and rolls back when it raises
    """

    with engine.begin() as conn:
        set_user(conn=conn)

        yield conn
