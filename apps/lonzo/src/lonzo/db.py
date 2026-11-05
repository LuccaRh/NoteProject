# Imports
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from lonzo.user import current_user


# Global variables
engine = create_async_engine(os.environ["LONZO_DATABASE_URL"])


# Code
async def set_user(conn: AsyncConnection) -> None:
    """
    Tells Postgres the user of the request until the transaction ends:
    the policies of the tables show and take only the rows of
    app.user_id (empty without a user, so no rows)
    """

    user_id = current_user.get()
    await conn.execute(
        text("SELECT set_config('app.user_id', :user_id, true)"),
        {"user_id": "" if user_id is None else str(user_id)},
    )


@asynccontextmanager
async def transaction() -> AsyncIterator[AsyncConnection]:
    """
    One connection from the pool, in a transaction of the request's user
    that commits at the end of the block and rolls back when it raises
    """

    async with engine.begin() as conn:
        await set_user(conn=conn)

        yield conn
