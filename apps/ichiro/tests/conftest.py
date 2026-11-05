# Imports
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection

from ichiro.db import engine
from ichiro.main import app
from ichiro.services import health, notes


# Global variables
ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"
USER = UUID("00000000-0000-7000-8000-000000000001")


# Code
# Run the migrations once, before the first test
@pytest.fixture(scope="session", autouse=True)
def migrate() -> None:

    # CI starts with an empty database: create the tables first
    command.upgrade(Config(ALEMBIC_INI), "head")


# One connection per test, rolled back so the dev database keeps none
@pytest.fixture
def conn(monkeypatch: pytest.MonkeyPatch) -> Iterator[Connection]:

    with engine.connect() as conn:
        outer = conn.begin()

        # Each transaction a savepoint, so a failed request spares the next
        @contextmanager
        def test_transaction() -> Iterator[Connection]:

            with conn.begin_nested():
                yield conn

        monkeypatch.setattr(health, "transaction", test_transaction)
        monkeypatch.setattr(notes, "transaction", test_transaction)

        yield conn

        outer.rollback()


# Client logged in as USER: the X-User-Id that Caddy would send
@pytest.fixture
def client(conn: Connection) -> TestClient:

    return TestClient(app, headers={"X-User-Id": str(USER)})

