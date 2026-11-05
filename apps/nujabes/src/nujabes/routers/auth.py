# Imports
from typing import Annotated

from fastapi import APIRouter, Cookie, Response

from nujabes.schemas.auth import Login, Session
from nujabes.services.sessions import find_session, log_in, log_out


# Global variables
router = APIRouter(prefix="/auth")
COOKIE = "session"
MAX_AGE = 30 * 24 * 60 * 60
SessionCookie = Annotated[str | None, Cookie(alias=COOKIE)]


# Code
@router.post("/login", status_code=204)
def post_login(login: Login, response: Response) -> None:
    """
    Logs in with email and password: the browser gets the session token
    in a cookie JavaScript can't read (httponly), sent only over HTTPS
    (secure) and not on requests started by other sites (samesite); it
    lasts the 30 days of a new session in the table
    """

    token = log_in(email=login.email, password=login.password)
    response.set_cookie(
        COOKIE,
        token,
        max_age=MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
    )


@router.get("/session")
def get_session(response: Response, session: SessionCookie = None) -> Session:
    """
    The user logged in with this cookie, also in the X-User-Id header:
    Caddy asks here before each notes or chat request (forward_auth) and
    passes the header on; 401 without a session
    """

    found = find_session(token=session)
    response.headers["X-User-Id"] = str(found.user_id)

    return found


@router.post("/logout", status_code=204)
def post_logout(response: Response, session: SessionCookie = None) -> None:
    """
    Ends the session of this cookie and tells the browser to drop it
    """

    log_out(token=session)
    response.delete_cookie(COOKIE, secure=True, httponly=True, samesite="lax")
