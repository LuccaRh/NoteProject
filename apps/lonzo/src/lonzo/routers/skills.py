# Imports
from typing import Literal
from uuid import UUID

from fastapi import APIRouter

from lonzo.schemas.notes import Note
from lonzo.schemas.skills import Skill, SkillAdd, SkillPublish, WorkspaceSkill
from lonzo.services.skills import (
    add_skill,
    list_skills,
    publish_skill,
    workspace_skills,
)


# Global variables
router = APIRouter(prefix="/chat")


# Code
@router.get("/skills")
async def get_skills(owner: Literal["me"] | None = None) -> list[Skill]:
    """
    The skills other people published; owner=me answers the person's
    """

    return await list_skills(mine=owner == "me")


@router.post("/skills")
async def post_skill(body: SkillPublish) -> Skill:
    """
    Publishes a skill note, or updates what it published before
    """

    return await publish_skill(note_id=body.note_id)


@router.get("/workspaces/{folder_id}/skills")
async def get_workspace_skills(folder_id: UUID) -> list[WorkspaceSkill]:
    """
    The skills of a workspace, with their titles and summaries
    """

    return await workspace_skills(folder_id=folder_id)


@router.post("/workspaces/{folder_id}/skills", status_code=201)
async def post_workspace_skill(folder_id: UUID, body: SkillAdd) -> Note:
    """
    Copies a skill to a workspace; answers the note created
    """

    return await add_skill(folder_id=folder_id, source=body)
