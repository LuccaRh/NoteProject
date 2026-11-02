# Imports
from uuid import UUID

from fastapi import APIRouter

from lonzo.schemas.conversations import Conversation, ConversationWithMessages
from lonzo.services.conversations import get_conversation, list_conversations


# Global variables
router = APIRouter(prefix="/chat/conversations")


# Code
@router.get("")
async def get_conversations(
    folder_id: UUID | None = None,
) -> list[Conversation]:
    """
    The conversations of the folder's workspace (without folder_id, of
    the root one), the most recently used first
    """

    return await list_conversations(folder_id=folder_id)


@router.get("/{conversation_id}")
async def get_one_conversation(
    conversation_id: UUID,
) -> ConversationWithMessages:
    """
    A conversation with all its messages, in order
    """

    return await get_conversation(conversation_id=conversation_id)
