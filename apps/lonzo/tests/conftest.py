# Imports
import asyncio
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine

from lonzo import db


# Global variables
ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


# Code
async def database_now() -> datetime:

    async with db.transaction() as conn:
        result = await conn.execute(text("SELECT clock_timestamp()"))
        now: datetime = result.scalar_one()

        return now


async def delete_since(start: datetime) -> None:

    async with db.transaction() as conn:
        await conn.execute(
            text("DELETE FROM conversations WHERE created_at >= :start"),
            {"start": start},
        )


# Runs the migrations once, before the first test (CI starts empty)
@pytest.fixture(scope="session", autouse=True)
def migrate() -> None:

    command.upgrade(Config(ALEMBIC_INI), "head")


# No pool (a connection can't change loops); deletes its conversations
@pytest.fixture(autouse=True)
def database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:

    engine = create_async_engine(db.engine.url, poolclass=NullPool)
    monkeypatch.setattr(db, "engine", engine)
    start = asyncio.run(database_now())

    yield

    asyncio.run(delete_since(start=start))
