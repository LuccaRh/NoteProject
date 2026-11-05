# Imports
from uuid import UUID

from conftest import EMAIL, PASSWORD
from fastapi.testclient import TestClient
from sqlalchemy import Connection, text


# Code
def log_in(client: TestClient) -> None:
    """
    Logs the client in as the test user
    """

    response = client.post(
        "/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert response.status_code == 204


def test_login_sets_a_session_cookie(
    client: TestClient,
    user_id: UUID,
) -> None:

    log_in(client=client)

    cookie = next(c for c in client.cookies.jar if c.name == "session")
    assert cookie.secure
    assert cookie.has_nonstandard_attr("HttpOnly")


def test_session_answers_the_user_id(
    client: TestClient,
    user_id: UUID,
) -> None:

    log_in(client=client)

    response = client.get("/auth/session")
    assert response.status_code == 200
    assert response.json() == {"user_id": str(user_id)}
    assert response.headers["X-User-Id"] == str(user_id)


def test_wrong_password_is_refused(
    client: TestClient,
    user_id: UUID,
) -> None:

    response = client.post(
        "/auth/login",
        json={"email": EMAIL, "password": "wrong"},
    )
    assert response.status_code == 401
    assert "session" not in client.cookies


def test_unknown_email_is_refused(
    client: TestClient,
    user_id: UUID,
) -> None:

    response = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": PASSWORD},
    )
    assert response.status_code == 401


def test_no_cookie_has_no_session(client: TestClient) -> None:

    response = client.get("/auth/session")
    assert response.status_code == 401
    assert "X-User-Id" not in response.headers


def test_made_up_cookie_has_no_session(client: TestClient) -> None:

    client.cookies.set("session", "made-up", domain="testserver.local")

    response = client.get("/auth/session")
    assert response.status_code == 401


def test_logout_ends_the_session(
    client: TestClient,
    user_id: UUID,
) -> None:

    log_in(client=client)
    token = client.cookies["session"]

    response = client.post("/auth/logout")
    assert response.status_code == 204
    assert "session" not in client.cookies

    # The old token no longer works, even if a copy of it was kept
    client.cookies.set("session", token, domain="testserver.local")
    response = client.get("/auth/session")
    assert response.status_code == 401


def test_expired_session_is_refused(
    client: TestClient,
    conn: Connection,
    user_id: UUID,
) -> None:

    log_in(client=client)
    conn.execute(text("UPDATE sessions SET expires_at = now()"))

    response = client.get("/auth/session")
    assert response.status_code == 401


def test_token_is_kept_only_as_a_hash(
    client: TestClient,
    conn: Connection,
    user_id: UUID,
) -> None:

    log_in(client=client)
    token = client.cookies["session"]

    stored = conn.execute(
        text("SELECT token_hash FROM sessions WHERE user_id = :id"),
        {"id": user_id},
    ).scalar_one()
    assert stored != token.encode()
    assert len(stored) == 32
