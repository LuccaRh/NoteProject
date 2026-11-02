# Imports
from fastapi import APIRouter

from lonzo.schemas.notes import Note
from lonzo.schemas.workspaces import WorkspaceRequest
from lonzo.services.workspaces import create_workspace


# Global variables
router = APIRouter(prefix="/chat/workspaces")


# Code
@router.post("", status_code=201)
async def post_workspace(body: WorkspaceRequest) -> list[Note]:
    """
    Turns a folder into a workspace from one text; answers every note
    created
    """

    return await create_workspace(
        folder_id=body.folder_id,
        description=body.description,
    )
