# Imports
from uuid import UUID

from pydantic import BaseModel


# Code
class Note(BaseModel):
    """
    The fields of an ichiro note that lonzo reads
    """

    id: UUID
    parent_id: UUID | None
    is_folder: bool
    title: str
    body: str


class NoteMatch(BaseModel):
    """
    A note found by the words in its title or body, never a folder
    """

    id: UUID
    title: str
    is_folder: bool = False


class TitleMatch(BaseModel):
    """
    A note or folder found by a piece of its title
    """

    id: UUID
    title: str
    is_folder: bool
