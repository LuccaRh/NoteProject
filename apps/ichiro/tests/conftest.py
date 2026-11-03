# Imports
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

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


# Code
# Run the migrations once, before the first test
@pytest.fixture(scope="session", autouse=True)
def migrate() -> None:

    # CI starts with an empty database: create the tables first
    command.upgrade(Config(ALEMBIC_INI), "head")


# Client whose requests share one connection, undone after the test
@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:

    # One transaction per test, rolled back so the dev database keeps none
    with engine.connect() as conn:
        outer = conn.begin()

        # Each transaction a savepoint, so a failed request spares the next
        @contextmanager
        def test_transaction() -> Iterator[Connection]:

            with conn.begin_nested():
                yield conn

        monkeypatch.setattr(health, "transaction", test_transaction)
        monkeypatch.setattr(notes, "transaction", test_transaction)

        yield TestClient(app)

        outer.rollback()
