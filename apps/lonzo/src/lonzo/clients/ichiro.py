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
WORKSPACE_FOLDERS = ["kb", "skills", "scripts", "hooks"]
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


async def find_note(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID | None,
    title: str,
) -> Note | None:
    """
    The note or folder with this title right inside a folder (None = the
    root), filtered by ichiro; titles are unique inside a folder
    """

    params = {"title": title}

    if parent_id is not None:
        params["parent_id"] = str(parent_id)

    response = await ichiro.get("/notes", params=params)
    response.raise_for_status()
    notes = TypeAdapter(list[Note]).validate_python(response.json())

    return notes[0] if notes else None


async def find_by_path(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID,
    path: str,
) -> Note | None:
    """
    The note or folder at a path of titles (a/b/c) inside parent_id,
    walked down by ichiro in one query; None when a name is missing
    """

    params = {"parent_id": str(parent_id), "path": path}
    response = await ichiro.get("/notes/by-path", params=params)

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return Note.model_validate(response.json())


async def find_workspace(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID | None,
) -> UUID | None:
    """
    The .workspace folder right inside a folder, if it has one
    """

    note = await find_note(ichiro=ichiro, parent_id=parent_id, title=WORKSPACE)

    if note is None or not note.is_folder:
        return None

    return note.id


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


async def get_note(ichiro: httpx2.AsyncClient, note_id: UUID) -> Note | None:
    """
    One note or folder by id; None when ichiro has no such note
    """

    response = await ichiro.get(f"/notes/{note_id}")

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return Note.model_validate(response.json())


async def create_note(
    ichiro: httpx2.AsyncClient,
    title: str,
    parent_id: UUID,
    body: str = "",
    is_folder: bool = False,
) -> Note:
    """
    A new note or folder inside parent_id, as ichiro saved it; ValueError
    when the folder already has that title (409)
    """

    note = {
        "title": title,
        "body": body,
        "parent_id": str(parent_id),
        "is_folder": is_folder,
    }
    response = await ichiro.post("/notes", json=note)

    if response.status_code == 409:
        raise ValueError(f"{title} already exists")

    response.raise_for_status()

    return Note.model_validate(response.json())


async def create_workspace_folders(
    ichiro: httpx2.AsyncClient,
    parent_id: UUID,
) -> list[Note]:
    """
    The .workspace folder that turns a folder into a workspace, then its
    empty subfolders (kb, skills, scripts, hooks); keeps the ones that
    already exist, so a retry reuses them, and answers the ones it created
    """

    created = []
    workspace = await find_note(
        ichiro=ichiro,
        parent_id=parent_id,
        title=WORKSPACE,
    )

    if workspace is None:
        workspace = await create_note(
            ichiro=ichiro,
            title=WORKSPACE,
            parent_id=parent_id,
            is_folder=True,
        )
        created.append(workspace)

    notes = await children(ichiro=ichiro, parent_id=workspace.id)
    titles = {note.title for note in notes}

    for title in WORKSPACE_FOLDERS:
        if title in titles:
            continue

        folder = await create_note(
            ichiro=ichiro,
            title=title,
            parent_id=workspace.id,
            is_folder=True,
        )
        created.append(folder)

    return created
