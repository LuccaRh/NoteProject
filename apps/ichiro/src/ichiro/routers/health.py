# Imports
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import Connection

from ichiro.db import get_conn
from ichiro.services.health import check_database


# Global variables
router = APIRouter()


# Code
@router.get("/health")
def health(conn: Annotated[Connection, Depends(get_conn)]) -> dict[str, str]:
    """
    Answers ok while the service and its database are up
    """

    check_database(conn=conn)

    return {"status": "ok"}
