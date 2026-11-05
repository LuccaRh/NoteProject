# Imports
import secrets

from nujabes.db import transaction
from nujabes.errors import NoSession, WrongLogin
from nujabes.repositories.sessions import (
    delete_session,
    insert_session,
    select_session_user_id,
)
from nujabes.repositories.users import select_user_id
from nujabes.schemas.auth import Session


# Code
def log_in(email: str, password: str) -> str:
    """
    Opens a session for the user with this email and password and
    returns its token; WrongLogin when they don't match a user
    """

    with transaction() as conn:
        user_id = select_user_id(conn=conn, email=email, password=password)

        if user_id is None:
            raise WrongLogin("wrong email or password")

        # 32 random bytes: too many to guess, even with many tries
        token = secrets.token_urlsafe(32)
        insert_session(conn=conn, token=token, user_id=user_id)

    return token


def find_session(token: str | None) -> Session:
    """
    The user of the session with this token; NoSession when there is no
    token, or no open session with it
    """

    if token is None:
        raise NoSession("not logged in")

    with transaction() as conn:
        user_id = select_session_user_id(conn=conn, token=token)

    if user_id is None:
        raise NoSession("not logged in")

    return Session(user_id=user_id)


def log_out(token: str | None) -> None:
    """
    Ends the session with this token; nothing to do without one
    """

    if token is None:
        return

    with transaction() as conn:
        delete_session(conn=conn, token=token)
