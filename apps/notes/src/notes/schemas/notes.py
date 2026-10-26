# Imports
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# Code
class Note(BaseModel):
    id: UUID
    parent_id: UUID | None
    is_folder: bool
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


class NoteCreate(BaseModel):
    title: str
    body: str = ""
    parent_id: UUID | None = None
    is_folder: bool = False


class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    parent_id: UUID | None = None
