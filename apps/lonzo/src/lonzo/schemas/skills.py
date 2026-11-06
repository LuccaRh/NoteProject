# Imports
from typing import Self
from uuid import UUID

from pydantic import BaseModel, model_validator


# Code
class Skill(BaseModel):
    """
    A published skill, as anyone reads it
    """

    id: UUID
    user_id: UUID
    title: str
    summary: str
    body: str


class WorkspaceSkill(BaseModel):
    """
    A skill of a workspace: the note that keeps it and its list line
    """

    id: UUID
    title: str
    summary: str


class SkillAdd(BaseModel):
    """
    Where the copy comes from: a published skill or one of the person's
    own skill notes, never both
    """

    skill_id: UUID | None = None
    note_id: UUID | None = None

    @model_validator(mode="after")
    def one_source(self) -> Self:
        """
        Refuses a request with no source, or with two
        """

        if (self.skill_id is None) == (self.note_id is None):
            raise ValueError("send skill_id or note_id")

        return self


class SkillPublish(BaseModel):
    """
    The skill note that goes public
    """

    note_id: UUID
