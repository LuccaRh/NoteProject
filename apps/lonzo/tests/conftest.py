# Imports
import asyncio
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fakes import OTHER_USER, USER
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine

from lonzo import db
from lonzo.user import current_user


# Global variables
ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


# Code
async def database_now() -> datetime:

    async with db.transaction() as conn:
        result = await conn.execute(text("SELECT clock_timestamp()"))
        now: datetime = result.scalar_one()

        return now


# Each user sees only their own rows: delete as each test user
async def delete_since(start: datetime) -> None:

    for user_id in (USER, OTHER_USER):
        current_user.set(user_id)

        async with db.transaction() as conn:
            await conn.execute(
                text("DELETE FROM conversations WHERE created_at >= :start"),
                {"start": start},
            )
            await conn.execute(text("DELETE FROM settings"))


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
