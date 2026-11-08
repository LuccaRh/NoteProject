# Imports
from datetime import date
from pathlib import Path
from uuid import UUID

from lonzo.core.connections import claude, ichiro
from lonzo.core.errors import FolderNotFound, NotAFolder
from lonzo.schemas.notes import Note
from lonzo.services.note_tools import NoteTools
from lonzo.services.settings import get_model_settings


# Global variables
WORKSPACE = ".workspace"
RULES = "CLAUDE.md"
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


async def find_skills_folder(workspace: UUID) -> UUID | None:
    """
    The skills folder of a .workspace, if it still has one
    """

    notes = await ichiro.list_notes(parent_id=workspace, title=SKILLS)

    if not notes or not notes[0].is_folder:
        return None

    return notes[0].id


async def create_skills_folder(workspace: UUID) -> UUID:
    """
    A new skills folder for a .workspace that lost it
    """

    folder = await ichiro.create_note(
        title=SKILLS,
        parent_id=workspace,
        is_folder=True,
    )

    return folder.id


def is_skill_path(path: str) -> bool:
    """
    Whether a path of titles ends right inside a skills folder of a
    .workspace
    """

    return path.split("/")[-3:-1] == [WORKSPACE, SKILLS]


def split_skill(body: str) -> tuple[str, str]:
    """
    The summary of a skill, its first line with text and without heading
    marks, and the rest of the body
    """

    first, _, rest = body.strip().partition("\n")

    return first.lstrip("# ").strip(), rest.strip()


async def skills_list(folder_id: UUID) -> list[str]:
    """
    The skills of a workspace, one line each with the id, the title and
    the summary, in one part; the bodies stay out and nothing comes back
    with no skills
    """

    lines = [
        f"- {note.id} {note.title}: {split_skill(body=note.body)[0]}"
        for note in await ichiro.list_notes(parent_id=folder_id)
        if not note.is_folder
    ]

    return ["# Skills\n\n" + "\n".join(lines)] if lines else []


async def workspace_rules(folder_id: UUID | None) -> str:
    """
    Rules for a question: the CLAUDE.md of each .workspace above the
    folder, from the root down, then the notes of the folder's own
    .workspace, as written (the CLAUDE.md opens saying they win), and the
    list of its skills; empty with no folder (the root never has one)
    """

    if folder_id is None:
        return ""

    path = f"{WORKSPACE}/{RULES}"
    above = await ichiro.list_notes_above(note_id=folder_id, path=path)
    workspace = await find_workspace(parent_id=folder_id)
    notes: list[Note] = []

    if workspace is not None:
        notes = await ichiro.list_notes(parent_id=workspace)

    parts = [
        f"# {note.title}\n\n{note.body}"
        for note in [*above, *notes]
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
