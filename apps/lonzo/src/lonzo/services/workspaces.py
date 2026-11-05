# Imports
from datetime import date
from pathlib import Path
from uuid import UUID

from lonzo.connections import claude, ichiro
from lonzo.errors import FolderNotFound, NotAFolder
from lonzo.schemas.notes import Note
from lonzo.services.note_tools import NoteTools


# Global variables
WORKSPACE = ".workspace"
SKILLS = "skills"
WORKSPACE_FOLDERS = ["kb", SKILLS, "scripts", "hooks"]
PROMPT_PATH = Path(__file__).parent.parent / "create_workspace.md"
BASE_PATH = Path(__file__).parent.parent / "base_rules.md"


# Code
def base_rules() -> str:
    """
    The rules of every question, the same for every person, so they stay
    in the cache
    """

    return BASE_PATH.read_text(encoding="utf-8")


async def find_workspace(parent_id: UUID) -> UUID | None:
    """
    The .workspace folder right inside a folder, if it has one; titles are
    unique inside a folder
    """

    notes = await ichiro.list_notes(parent_id=parent_id, title=WORKSPACE)

    if not notes or not notes[0].is_folder:
        return None

    return notes[0].id


async def skills_list(folder_id: UUID) -> list[str]:
    """
    The skills of a workspace, one line each with the id, the title and
    the first line of the body, in one part; the bodies stay out and
    nothing comes back with no skills
    """

    lines = [
        f"- {note.id} {note.title}: {note.body.partition("\n")[0]}"
        for note in await ichiro.list_notes(parent_id=folder_id)
        if not note.is_folder
    ]

    return ["# Skills\n\n" + "\n".join(lines)] if lines else []


async def workspace_rules(folder_id: UUID | None) -> str:
    """
    Rules for a question: notes of the folder's .workspace, as written
    (the CLAUDE.md opens saying they win), and the list of its skills;
    empty with no folder or no .workspace (the root never has one)
    """

    if folder_id is None:
        return ""

    workspace = await find_workspace(parent_id=folder_id)

    if workspace is None:
        return ""

    notes = await ichiro.list_notes(parent_id=workspace)
    parts = [
        f"# {note.title}\n\n{note.body}"
        for note in notes
        if not note.is_folder
    ]

    for note in notes:

        if note.is_folder and note.title == SKILLS:
            parts.extend(await skills_list(folder_id=note.id))

    return "\n\n".join(parts)


async def question_context(folder_id: UUID | None) -> str:
    """
    What changes with the question: today's date, the folder of the
    conversation by its path from the root, and the rules of its workspace
    """

    path = "/"

    if folder_id is not None:
        folder = await ichiro.get_note_path(note_id=folder_id)
        path = "/" if folder is None else f"/{folder.path}"

    place = f"Today is {date.today().isoformat()}. Current folder: {path}"
    rules = await workspace_rules(folder_id=folder_id)

    return f"{place}\n\n{rules}" if rules else place


async def create_workspace_folders(parent_id: UUID) -> list[Note]:
    """
    The .workspace folder that turns a folder into a workspace, then its
    empty subfolders (kb, skills, scripts, hooks); keeps the ones that
    already exist, so a retry reuses them, and answers the ones it created
    """

    created = []
    notes = await ichiro.list_notes(parent_id=parent_id, title=WORKSPACE)

    if notes:
        workspace = notes[0]
    else:
        workspace = await ichiro.create_note(
            title=WORKSPACE,
            parent_id=parent_id,
            is_folder=True,
        )
        created.append(workspace)

    notes = await ichiro.list_notes(parent_id=workspace.id)
    titles = {note.title for note in notes}

    for title in WORKSPACE_FOLDERS:
        if title in titles:
            continue

        folder = await ichiro.create_note(
            title=title,
            parent_id=workspace.id,
            is_folder=True,
        )
        created.append(folder)

    return created


async def create_workspace(folder_id: UUID, description: str) -> list[Note]:
    """
    Turns a folder into a workspace from one text: creates .workspace/ and
    its subfolders, then the model saves the CLAUDE.md and any kb notes,
    skills, scripts and hooks with tools; answers every note created.
    What was saved stays when it fails, and a retry reuses it
    """

    claude.check_key()
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
    await claude.run_tools(system=system, request=request, tools=notes.tools())

    return [*folders, *notes.created]
