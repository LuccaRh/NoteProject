# Imports
from datetime import date
from pathlib import Path
from uuid import UUID

from lonzo.core.connections import claude, ichiro
from lonzo.core.errors import FolderNotFound, NotAFolder
from lonzo.schemas.notes import Note
from lonzo.services.note_tools import NoteTools
from lonzo.services.settings import get_model_settings
from lonzo.services.workspaces import create_workspace_folders


# Global variables
PROMPT_PATH = Path(__file__).parent.parent / "create_workspace.md"


# Code
async def create_workspace(folder_id: UUID, description: str) -> list[Note]:
    """
    Turns a folder into a workspace from one text: creates .workspace/ and
    its subfolders, then the model saves the CLAUDE.md and any kb notes,
    skills, scripts and hooks with tools; answers every note created.
    What was saved stays when it fails, and a retry reuses it
    """

    settings = await get_model_settings()
    folder = await ichiro.get_note_path(note_id=folder_id)

    if folder is None:
        raise FolderNotFound("folder not found")

    if not folder.is_folder:
        raise NotAFolder("folder_id is not a folder")

    folders = await create_workspace_folders(parent_id=folder.id)
    notes = NoteTools()

    # A fixed system prompt keeps the cache; date and folder go in the request
    system = PROMPT_PATH.read_text(encoding="utf-8")
    request = (
        f"Today is {date.today().isoformat()}. The workspace folder is"
        f" /{folder.path}.\n\n{description}"
    )
    await claude.run_tools(
        settings=settings,
        system=system,
        request=request,
        tools=notes.tools(),
    )

    return [*folders, *notes.created]
