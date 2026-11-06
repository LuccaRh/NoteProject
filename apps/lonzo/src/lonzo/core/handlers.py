# Imports
import httpx2
from anthropic import APIError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lonzo.core.errors import (
    ConversationNotFound,
    FolderNotFound,
    InvalidApiKey,
    InvalidSettings,
    MissingApiKey,
    NotAFolder,
)


# Global variables
STATUS: dict[type[Exception], int] = {
    APIError: 502,
    MissingApiKey: 422,
    InvalidApiKey: 422,
    InvalidSettings: 422,
    FolderNotFound: 404,
    NotAFolder: 422,
    ConversationNotFound: 404,
}


# Code
async def known_error(request: Request, error: Exception) -> JSONResponse:
    """
    Answers an error from STATUS with its status (the first kind it is
    an instance of, so subclasses of APIError too) and its message
    """

    status = next(
        code for kind, code in STATUS.items() if isinstance(error, kind)
    )

    return JSONResponse({"detail": str(error)}, status)


async def notes_unavailable(
    request: Request,
    error: Exception,
) -> JSONResponse:
    """
    502 when ichiro is down or answers an error lonzo did not expect
    """

    return JSONResponse({"detail": "notes service unavailable"}, 502)


def add_handlers(app: FastAPI) -> None:
    """
    Registers known_error for every error in STATUS, and
    notes_unavailable for the errors of the calls to ichiro
    """

    for error in STATUS:
        app.add_exception_handler(error, known_error)

    app.add_exception_handler(httpx2.HTTPError, notes_unavailable)
