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
