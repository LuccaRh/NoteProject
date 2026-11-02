# Imports
import json
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from lonzo.schemas.conversations import Conversation, Message, Role


# Global variables
CONVERSATION_COLUMNS = "id, folder_id, title, created_at, updated_at"
MESSAGE_COLUMNS = "id, role, content, created_at"


# Code
async def insert_conversation(
    conn: AsyncConnection,
    folder_id: UUID | None,
    title: str,
) -> Conversation:
    """
    A new conversation, still empty, in the workspace of folder_id
    """

    result = await conn.execute(
        text(
            "INSERT INTO conversations (folder_id, title)"
            " VALUES (:folder_id, :title)"
            f" RETURNING {CONVERSATION_COLUMNS}"
        ),
        {"folder_id": folder_id, "title": title},
    )

    return Conversation.model_validate(result.mappings().one())


async def select_conversation(
    conn: AsyncConnection,
    conversation_id: UUID,
) -> Conversation | None:
    """
    The conversation with that id; None when it doesn't exist
    """

    result = await conn.execute(
        text(
            f"SELECT {CONVERSATION_COLUMNS} FROM conversations WHERE id = :id"
        ),
        {"id": conversation_id},
    )
    row = result.mappings().one_or_none()

    if row is None:
        return None

    return Conversation.model_validate(row)


async def select_conversations(
    conn: AsyncConnection,
    folder_id: UUID | None,
) -> list[Conversation]:
    """
    The conversations of one workspace, the most recently used first
    """

    # "= NULL" matches nothing: the root workspace needs IS NULL
    where = "folder_id IS NULL" if folder_id is None else "folder_id = :id"
    result = await conn.execute(
        text(
            f"SELECT {CONVERSATION_COLUMNS} FROM conversations"
            f" WHERE {where} ORDER BY updated_at DESC"
        ),
        {"id": folder_id},
    )

    return [Conversation.model_validate(row) for row in result.mappings()]


async def select_messages(
    conn: AsyncConnection,
    conversation_id: UUID,
) -> list[Message]:
    """
    The messages of a conversation, in the order they were said (uuidv7
    ids grow with time)
    """

    result = await conn.execute(
        text(
            f"SELECT {MESSAGE_COLUMNS} FROM messages"
            " WHERE conversation_id = :id ORDER BY id"
        ),
        {"id": conversation_id},
    )

    return [Message.model_validate(row) for row in result.mappings()]


async def insert_message(
    conn: AsyncConnection,
    conversation_id: UUID,
    role: Role,
    content: list[dict[str, Any]],
) -> None:
    """
    Adds a message to a conversation and marks the conversation as just
    used, so it goes to the top of its list
    """

    await conn.execute(
        text(
            "INSERT INTO messages (conversation_id, role, content)"
            " VALUES (:id, :role, CAST(:content AS jsonb))"
        ),
        {"id": conversation_id, "role": role, "content": json.dumps(content)},
    )
    await conn.execute(
        text("UPDATE conversations SET updated_at = now() WHERE id = :id"),
        {"id": conversation_id},
    )
