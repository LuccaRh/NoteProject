# Imports
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection

from ichiro.db import engine, get_conn
from ichiro.main import app


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
def client() -> Iterator[TestClient]:

    # One transaction per test, rolled back at the end: the database
    # (the dev one, on the host) keeps no test rows
    with engine.connect() as conn:
        outer = conn.begin()

        # Replaces get_conn: each request in a savepoint of the shared
        # connection, so a failed one doesn't break the next
        def test_conn() -> Iterator[Connection]:

            with conn.begin_nested():
                yield conn

        app.dependency_overrides[get_conn] = test_conn

        yield TestClient(app)

        app.dependency_overrides.clear()
        outer.rollback()
