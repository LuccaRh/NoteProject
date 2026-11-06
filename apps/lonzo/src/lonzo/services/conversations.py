# Imports
from uuid import UUID

from lonzo.core.db import transaction
from lonzo.core.errors import ConversationNotFound
from lonzo.repositories.conversations import (
    insert_conversation,
    insert_message,
    select_conversation,
    select_conversations,
    select_messages,
)
from lonzo.schemas.conversations import (
    Conversation,
    ConversationWithMessages,
    Turn,
)


# Global variables
TITLE_LENGTH = 80


# Code
async def start_conversation(
    folder_id: UUID | None,
    question: str,
) -> Conversation:
    """
    A new conversation in the workspace of folder_id, titled with the
    start of its first question
    """

    title = question.strip()[:TITLE_LENGTH]

    async with transaction() as conn:
        return await insert_conversation(
            conn=conn,
            folder_id=folder_id,
            title=title,
        )


async def list_conversations(folder_id: UUID | None) -> list[Conversation]:
    """
    The conversations of one workspace, the most recently used first
    """

    async with transaction() as conn:
        return await select_conversations(conn=conn, folder_id=folder_id)


async def get_conversation(conversation_id: UUID) -> ConversationWithMessages:
    """
    The conversation with all its messages; ConversationNotFound when the
    id is not one
    """

    async with transaction() as conn:
        conversation = await select_conversation(
            conn=conn,
            conversation_id=conversation_id,
        )

        if conversation is None:
            raise ConversationNotFound("conversation not found")

        messages = await select_messages(
            conn=conn,
            conversation_id=conversation_id,
        )

    return ConversationWithMessages(
        **conversation.model_dump(),
        messages=messages,
    )


async def save_exchange(
    conversation_id: UUID,
    question: str,
    turns: list[Turn],
) -> None:
    """
    Keeps a question and the turns of its answer, tool calls and results
    included, all or none, in the shape the API takes them back
    """

    async with transaction() as conn:
        await insert_message(
            conn=conn,
            conversation_id=conversation_id,
            role="user",
            content=[{"type": "text", "text": question}],
        )

        for role, content in turns:
            await insert_message(
                conn=conn,
                conversation_id=conversation_id,
                role=role,
                content=content,
            )
