# Imports
from typing import Annotated

import httpx2
from anthropic import APIError, AsyncAnthropic
from fastapi import APIRouter, Depends, HTTPException

from lonzo.clients.anthropic import get_client, write_workspace
from lonzo.clients.ichiro import (
    create_workspace_folders,
    get_ichiro,
    get_note,
)
from lonzo.schemas.notes import Note
from lonzo.schemas.workspaces import WorkspaceRequest
from lonzo.tools import NoteTools


# Global variables
router = APIRouter(prefix="/chat/workspaces")


# Code
@router.post("", status_code=201)
async def create_workspace(
    body: WorkspaceRequest,
    client: Annotated[AsyncAnthropic, Depends(get_client)],
    ichiro: Annotated[httpx2.AsyncClient, Depends(get_ichiro)],
) -> list[Note]:
    """
    Turns a folder into a workspace from one text: lonzo creates .workspace/
    and its subfolders through ichiro, then the model saves the CLAUDE.md
    and any kb notes, skills, scripts and hooks with tools; answers every
    note created. What was saved stays when it fails, and a retry reuses it
    """

    folder = await get_note(ichiro=ichiro, note_id=body.folder_id)

    if folder is None:
        raise HTTPException(404, "folder not found")

    if not folder.is_folder:
        raise HTTPException(422, "folder_id is not a folder")

    folders = await create_workspace_folders(ichiro=ichiro, parent_id=folder.id)
    notes = NoteTools(ichiro=ichiro, root_id=folder.id)

    try:
        await write_workspace(
            client=client,
            description=body.description,
            tools=notes.tools(),
        )
    except APIError as error:
        raise HTTPException(502, error.message)

    return [*folders, *notes.created]
