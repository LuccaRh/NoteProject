# Imports
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ichiro.errors import (
    FieldNull,
    NoteNotFound,
    ParentInsideNote,
    ParentNotAFolder,
    ParentNotFound,
    PathEmpty,
    TitleTaken,
)


# Global variables
STATUS: dict[type[Exception], int] = {
    NoteNotFound: 404,
    ParentNotFound: 422,
    ParentNotAFolder: 422,
    ParentInsideNote: 422,
    PathEmpty: 422,
    FieldNull: 422,
    TitleTaken: 409,
}


# Code
async def domain_error(request: Request, error: Exception) -> JSONResponse:
    """
    Answers a domain error with its status from STATUS and its message
    as the detail
    """

    return JSONResponse({"detail": str(error)}, STATUS[type(error)])


def add_handlers(app: FastAPI) -> None:
    """
    Registers domain_error for every error in STATUS
    """

    for error in STATUS:
        app.add_exception_handler(error, domain_error)
