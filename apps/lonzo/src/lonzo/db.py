# Imports
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine


# Global variables
engine = create_async_engine(os.environ["LONZO_DATABASE_URL"])


# Code
@asynccontextmanager
async def transaction() -> AsyncIterator[AsyncConnection]:
    """
    One connection from the pool, in a transaction that commits at the end
    of the block and rolls back when it raises
    """

    async with engine.begin() as conn:
        yield conn
