# Imports
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from lonzo.schemas.skills import Skill


# Global variables
COLUMNS = "id, user_id, title, summary, body"


# Code
async def select_skills(
    conn: AsyncConnection,
    user_id: UUID | None,
    mine: bool,
) -> list[Skill]:
    """
    The published skills by title: those of user_id, or everyone else's
    """

    result = await conn.execute(
        text(
            f"SELECT {COLUMNS} FROM skills"
            " WHERE (user_id = :user_id) = :mine"
            " ORDER BY title"
        ),
        {"user_id": user_id, "mine": mine},
    )

    return [Skill.model_validate(row) for row in result.mappings()]


async def select_skill(conn: AsyncConnection, skill_id: UUID) -> Skill | None:
    """
    One published skill, or None
    """

    result = await conn.execute(
        text(f"SELECT {COLUMNS} FROM skills WHERE id = :skill_id"),
        {"skill_id": skill_id},
    )
    row = result.mappings().one_or_none()

    if row is None:
        return None

    return Skill.model_validate(row)


async def upsert_skill(
    conn: AsyncConnection,
    note_id: UUID,
    title: str,
    summary: str,
    body: str,
) -> Skill:
    """
    Publishes a note, or updates the row that came from it
    """

    result = await conn.execute(
        text(
            "INSERT INTO skills (note_id, title, summary, body)"
            " VALUES (:note_id, :title, :summary, :body)"
            " ON CONFLICT (user_id, note_id) DO UPDATE SET"
            " title = EXCLUDED.title,"
            " summary = EXCLUDED.summary,"
            " body = EXCLUDED.body"
            f" RETURNING {COLUMNS}"
        ),
        {"note_id": note_id, "title": title, "summary": summary, "body": body},
    )

    return Skill.model_validate(result.mappings().one())
