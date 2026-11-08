# Imports
from uuid import UUID

from lonzo.core.connections import ichiro
from lonzo.core.db import transaction
from lonzo.core.errors import NotASkill, NotAWorkspace, SkillNotFound
from lonzo.core.user import current_user
from lonzo.repositories.skills import select_skill, select_skills, upsert_skill
from lonzo.schemas.notes import Note
from lonzo.schemas.skills import Skill, SkillAdd, WorkspaceSkill
from lonzo.services.workspaces import (
    create_skills_folder,
    find_skills_folder,
    find_workspace,
    is_skill_path,
    skill_text,
    split_skill,
)


# Code
async def list_skills(mine: bool) -> list[Skill]:
    """
    The skills the person published, or the ones everyone else did
    """

    user_id = current_user.get()

    async with transaction() as conn:
        return await select_skills(conn=conn, user_id=user_id, mine=mine)


async def workspace_skills(folder_id: UUID) -> list[WorkspaceSkill]:
    """
    The skills of a workspace; empty when the folder is not one
    """

    workspace = await find_workspace(parent_id=folder_id)
    folder = None

    if workspace is not None:
        folder = await find_skills_folder(workspace=workspace)

    if folder is None:
        return []

    return [
        WorkspaceSkill(
            id=note.id,
            title=note.title,
            summary=split_skill(body=note.body)[0],
        )
        for note in await ichiro.list_notes(parent_id=folder)
        if not note.is_folder
    ]


async def load_skill_note(note_id: UUID) -> Note:
    """
    A note kept in a skills folder of the person; ichiro only shows their
    own notes, so an id of someone else's is a NotASkill too
    """

    path = await ichiro.get_note_path(note_id=note_id)
    note = None

    if path is not None and is_skill_path(path=path.path):
        note = await ichiro.get_note(note_id=note_id)

    if note is None or note.is_folder:
        raise NotASkill("note is not a skill")

    return note


async def add_skill(folder_id: UUID, source: SkillAdd) -> Note:
    """
    Copies a published skill or a skill note to the skills folder of a
    workspace; the copy has no tie to where it came from
    """

    workspace = await find_workspace(parent_id=folder_id)

    if workspace is None:
        raise NotAWorkspace("folder is not a workspace")

    if source.note_id is not None:
        note = await load_skill_note(note_id=source.note_id)
        title, body = note.title, note.body
    else:
        title, body = await published_text(skill_id=source.skill_id)

    folder = await find_skills_folder(workspace=workspace)

    if folder is None:
        folder = await create_skills_folder(workspace=workspace)

    return await ichiro.create_note(title=title, parent_id=folder, body=body)


async def published_text(skill_id: UUID | None) -> tuple[str, str]:
    """
    The title and the note body of a published skill, the summary in its
    header; the transaction ends before any call to ichiro
    """

    skill = None

    if skill_id is not None:
        async with transaction() as conn:
            skill = await select_skill(conn=conn, skill_id=skill_id)

    if skill is None:
        raise SkillNotFound("skill not found")

    body = skill_text(title=skill.title, summary=skill.summary, body=skill.body)

    return skill.title, body


async def publish_skill(note_id: UUID) -> Skill:
    """
    Publishes a skill note, or updates what it published before
    """

    note = await load_skill_note(note_id=note_id)
    summary, body = split_skill(body=note.body)

    if not summary:
        raise NotASkill("the skill is empty")

    async with transaction() as conn:
        return await upsert_skill(
            conn=conn,
            note_id=note.id,
            title=note.title,
            summary=summary,
            body=body,
        )
