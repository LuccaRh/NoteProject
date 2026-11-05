# Imports
from uuid import UUID

from sqlalchemy import Connection, text


# Code
def insert_session(conn: Connection, token: str, user_id: UUID) -> None:
    """
    Keeps a new session of the user, stored by the hash of its token
    """

    conn.execute(
        text(
            "INSERT INTO sessions (token_hash, user_id)"
            " VALUES (digest(:token, 'sha256'), :user_id)"
        ),
        {"token": token, "user_id": user_id},
    )


def select_session_user_id(conn: Connection, token: str) -> UUID | None:
    """
    Id of the user of the session with this token; None when there is
    no such session or it expired
    """

    return conn.execute(
        text(
            "SELECT user_id FROM sessions"
            " WHERE token_hash = digest(:token, 'sha256')"
            " AND expires_at > now()"
        ),
        {"token": token},
    ).scalar_one_or_none()


def delete_session(conn: Connection, token: str) -> None:
    """
    Ends the session with this token, if there is one
    """

    conn.execute(
        text(
            "DELETE FROM sessions"
            " WHERE token_hash = digest(:token, 'sha256')"
        ),
        {"token": token},
    )
