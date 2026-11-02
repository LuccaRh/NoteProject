# Imports
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# Code
class Note(BaseModel):
    """
    A note or folder as the table keeps it
    """

    id: UUID
    parent_id: UUID | None
    is_folder: bool
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


class NoteCreate(BaseModel):
    """
    Body of POST /notes: a note at the root unless parent_id is given
    """

    title: str
    body: str = ""
    parent_id: UUID | None = None
    is_folder: bool = False


class NoteUpdate(BaseModel):
    """
    Body of PATCH /notes/{id}: only the fields sent change
    """

    title: str | None = None
    body: str | None = None
    parent_id: UUID | None = None


class NotePath(BaseModel):
    """
    A note or folder inside another, by its path of titles from there
    """

    id: UUID
    path: str
    is_folder: bool


class NoteMatch(BaseModel):
    """
    A note found by a search, only what is needed to pick and open it
    """

    id: UUID
    title: str
