# Imports
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from uuid import UUID

from fastapi import Request, Response
from fastapi.responses import JSONResponse


# Global variables
current_user: ContextVar[UUID | None] = ContextVar("current_user", default=None)
Next = Callable[[Request], Awaitable[Response]]


# Code
async def read_user(request: Request, call_next: Next) -> Response:
    """
    Keeps the X-User-Id that Caddy got from nujabes (forward_auth) for
    the transactions of this request; 401 without a valid one, except on
    /health
    """

    if request.url.path == "/health":
        return await call_next(request)

    try:
        user_id = UUID(request.headers.get("X-User-Id", ""))
    except ValueError:
        return JSONResponse({"detail": "not logged in"}, 401)

    current_user.set(user_id)

    return await call_next(request)
