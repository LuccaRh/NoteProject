from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import Connection, text

from notes.db import get_conn


router = APIRouter()


@router.get("/health")
def health(conn: Annotated[Connection, Depends(get_conn)]) -> dict[str, str]:
    conn.execute(text("SELECT 1"))
    return {"status": "ok"}
