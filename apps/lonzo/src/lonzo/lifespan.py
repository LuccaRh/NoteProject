# Imports
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from lonzo.connections import claude, ichiro


# Code
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    What runs when the app starts and stops: on the way out, closes the
    connections kept open to ichiro and to the Anthropic API
    """

    yield
    await ichiro.close()
    await claude.close()
