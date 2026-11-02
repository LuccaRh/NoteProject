# Imports
from uuid import UUID

from pydantic import BaseModel, Field


# Code
class WorkspaceRequest(BaseModel):
    """
    What the person sends: the folder that becomes a workspace and one
    text about what they want from it
    """

    folder_id: UUID
    description: str = Field(min_length=1)
