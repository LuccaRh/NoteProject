# Imports
import httpx2
from anthropic import APIError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lonzo.errors import FolderNotFound, MissingApiKey, NotAFolder
from lonzo.lifespan import lifespan
from lonzo.routers import chat, health, workspaces


# Global variables
app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(chat.router)


# Code
@app.exception_handler(httpx2.HTTPError)
async def notes_unavailable(
    request: Request,
    error: httpx2.HTTPError,
) -> JSONResponse:
    """
    502 when ichiro is down or answers an error lonzo did not expect
    """

    return JSONResponse({"detail": "notes service unavailable"}, 502)


@app.exception_handler(APIError)
async def model_unavailable(request: Request, error: APIError) -> JSONResponse:
    """
    502 when the Anthropic API answers an error before any event went out
    """

    return JSONResponse({"detail": error.message}, 502)


@app.exception_handler(MissingApiKey)
async def missing_key(request: Request, error: MissingApiKey) -> JSONResponse:
    """
    503 while the service has no key for the Anthropic API
    """

    return JSONResponse({"detail": str(error)}, 503)


@app.exception_handler(FolderNotFound)
async def folder_not_found(
    request: Request,
    error: FolderNotFound,
) -> JSONResponse:
    """
    404 when the folder asked for does not exist
    """

    return JSONResponse({"detail": str(error)}, 404)


@app.exception_handler(NotAFolder)
async def not_a_folder(request: Request, error: NotAFolder) -> JSONResponse:
    """
    422 when the id asked for is a note, not a folder
    """

    return JSONResponse({"detail": str(error)}, 422)
