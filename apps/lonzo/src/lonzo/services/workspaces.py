# Imports
from datetime import date
from pathlib import Path
from uuid import UUID

from lonzo.core.connections import ichiro
from lonzo.schemas.notes import Note


# Global variables
WORKSPACE = ".workspace"
RULES = "CLAUDE.md"
SKILLS = "skills"
WORKSPACE_FOLDERS = ["kb", SKILLS, "scripts", "hooks"]
HEADER = "---"
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


def skill_header(body: str) -> tuple[str, str] | None:
    """
    The description in the --- header that opens a skill and the text after
    the header; None when it has no header or no description in it
    """

    lines = body.strip().split("\n")
    marks = [line.strip() for line in lines]

    if marks[0] != HEADER or HEADER not in marks[1:]:
        return None

    end = marks.index(HEADER, 1)

    for line in marks[1:end]:
        key, _, value = line.partition(":")
        value = value.strip()

        if value[:1] in ('"', "'") and value[:1] == value[-1:]:
            value = value[1:-1]

        if key == "description" and value:
            return value, "\n".join(lines[end + 1:]).strip()

    return None


def split_skill(body: str) -> tuple[str, str]:
    """
    The summary of a skill and the rest of its body: the description of its
    header, or its first line without heading marks when it has no header
    """

    header = skill_header(body=body)

    if header is not None:
        return header

    first, _, rest = body.strip().partition("\n")

    return first.lstrip("# ").strip(), rest.strip()


def skill_text(title: str, summary: str, body: str) -> str:
    """
    The text of a skill note: the header with its name and description,
    then the instructions
    """

    header = f"{HEADER}\nname: {title}\ndescription: {summary}\n{HEADER}"

    return f"{header}\n\n{body}".strip()


async def skill_notes(folder_id: UUID, above: bool = False) -> list[Note]:
    """
    The skill notes of the folder's own .workspace; with above, after the
    ones of each .workspace above it, from the root down
    """

    path = f"{WORKSPACE}/{SKILLS}"
    folders: list[Note] = []

    if above:
        folders = await ichiro.list_notes_above(note_id=folder_id, path=path)

    own = await ichiro.get_note_by_path(parent_id=folder_id, path=path)

    if own is not None:
        folders.append(own)

    return [
        note
        for folder in folders
        if folder.is_folder
        for note in await ichiro.list_notes(parent_id=folder.id)
        if not note.is_folder
    ]


async def find_skill(folder_id: UUID | None, name: str) -> Note | None:
    """
    The skill titled name that a folder can use, the closest one when more
    than one has the title; None with no folder or no such skill
    """

    if folder_id is None:
        return None

    notes = await skill_notes(folder_id=folder_id, above=True)

    return next((n for n in reversed(notes) if n.title == name), None)


async def skills_list(folder_id: UUID) -> list[str]:
    """
    The skills a folder can use, its own and the ones above it, one line
    each with the title and the summary, in one part; the bodies stay out
    and nothing comes back with no skills
    """

    lines = [
        f"- {note.title}: {split_skill(body=note.body)[0]}"
        for note in await skill_notes(folder_id=folder_id, above=True)
    ]

    return ["# Skills\n\n" + "\n".join(lines)] if lines else []


async def workspace_rules(folder_id: UUID | None) -> str:
    """
    Rules for a question: the CLAUDE.md of each .workspace above the
    folder, from the root down, then the notes of the folder's own
    .workspace, as written (the CLAUDE.md opens saying they win), and the
    list of the skills it can use; empty with no folder (the root never
    has one)
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

    parts.extend(await skills_list(folder_id=folder_id))

    return "\n\n".join(parts)


async def question_context(folder_id: UUID | None) -> str:
    """
    What the app tells the model before the conversation, in a block of
    its own: today's date, the folder by its path from the root, and the
    rules of its workspace
    """

    path = "/"

    if folder_id is not None:
        folder = await ichiro.get_note_path(note_id=folder_id)
        path = "/" if folder is None else f"/{folder.path}"

    place = f"Today is {date.today().isoformat()}. Current folder: {path}"
    rules = await workspace_rules(folder_id=folder_id)

    text = f"{place}\n\n{rules}" if rules else place

    return f"<context>\n{text}\n</context>"


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
