# Imports
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import Connection

from ichiro.db import get_conn
from ichiro.repositories.health import select_one


# Global variables
router = APIRouter()


# Code
@router.get("/health")
def health(conn: Annotated[Connection, Depends(get_conn)]) -> dict[str, str]:
    """
    Answers ok while the service and its database are up
    """

    select_one(conn=conn)

    return {"status": "ok"}
