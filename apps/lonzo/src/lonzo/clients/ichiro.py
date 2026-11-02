# Imports
import os
from collections.abc import AsyncIterator
from uuid import UUID

import httpx2
from pydantic import TypeAdapter

from lonzo.schemas.notes import Note


# Global variables
ICHIRO_URL = os.environ.get("ICHIRO_URL", "http://ichiro:8000")
WORKSPACE = ".workspace"
RULES_HEADER = (
    "These notes are the person's workspace. Follow them in every answer;"
    " they win over your own defaults (language, length, format)."
)


# Code
async def get_ichiro() -> AsyncIterator[httpx2.AsyncClient]:
    """
    Client of the notes service, straight through the compose network
    """

    async with httpx2.AsyncClient(base_url=ICHIRO_URL) as ichiro:
        yield ichiro


async def children(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID | None,
) -> list[Note]:
    """
    Notes and folders right inside a folder (None = the root)
    """

    params = {} if parent_id is None else {"parent_id": str(parent_id)}
    response = await ichiro.get("/notes", params=params)
    response.raise_for_status()

    return TypeAdapter(list[Note]).validate_python(response.json())


async def find_workspace(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID | None,
) -> UUID | None:
    """
    The .workspace folder right inside a folder, if it has one
    """

    for note in await children(ichiro=ichiro, parent_id=parent_id):
        if note.is_folder and note.title == WORKSPACE:
            return note.id

    return None


async def workspace_rules(
    ichiro: httpx2.AsyncClient,
    folder_id: UUID | None,
) -> str:
    """
    Rules for a question: notes of the root .workspace, then the
    folder's; empty when neither has one
    """

    parts = []
    folders = [None] if folder_id is None else [None, folder_id]

    for folder in folders:
        workspace = await find_workspace(ichiro=ichiro, parent_id=folder)

        if workspace is None:
            continue

        for note in await children(ichiro=ichiro, parent_id=workspace):
            if not note.is_folder:
                parts.append(f"# {note.title}\n\n{note.body}")

    if not parts:
        return ""

    return "\n\n".join([RULES_HEADER, *parts])
