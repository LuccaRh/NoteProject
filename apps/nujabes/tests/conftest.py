# Imports
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection, text

from nujabes.db import engine
from nujabes.main import app
from nujabes.services import sessions


# Global variables
ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"
EMAIL = "ana@example.com"
PASSWORD = "right password"


# Code
# Run the migrations once, before the first test
@pytest.fixture(scope="session", autouse=True)
def migrate() -> None:

    # CI starts with an empty database: create the tables first
    command.upgrade(Config(ALEMBIC_INI), "head")


# One connection per test, rolled back so the dev database keeps nothing
@pytest.fixture
def conn() -> Iterator[Connection]:

    with engine.connect() as conn:
        outer = conn.begin()

        yield conn

        outer.rollback()


# Client whose requests run in savepoints of the test connection
@pytest.fixture
def client(
    conn: Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:

    # Each transaction a savepoint, so a failed request spares the next
    @contextmanager
    def test_transaction() -> Iterator[Connection]:

        with conn.begin_nested():
            yield conn

    monkeypatch.setattr(sessions, "transaction", test_transaction)

    # https: the session cookie is secure, never sent over plain http
    return TestClient(app, base_url="https://testserver")


# A user added the way it is done by hand, with crypt() in the insert
@pytest.fixture
def user_id(conn: Connection) -> UUID:

    found: UUID = conn.execute(
        text(
            "INSERT INTO users (email, password_hash)"
            " VALUES (:email, crypt(:password, gen_salt('bf')))"
            " RETURNING id"
        ),
        {"email": EMAIL, "password": PASSWORD},
    ).scalar_one()

    return found
