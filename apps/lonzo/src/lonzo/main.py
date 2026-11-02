# Imports
import httpx2
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lonzo.routers import chat, health


# Global variables
app = FastAPI()
app.include_router(health.router)
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
