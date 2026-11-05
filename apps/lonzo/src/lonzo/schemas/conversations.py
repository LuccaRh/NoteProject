# Imports
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel


# Global variables
Role = Literal["user", "assistant"]
Turn = tuple[Role, list[dict[str, Any]]]


# Code
class Conversation(BaseModel):
    """
    A conversation of one workspace, without its messages; folder_id None
    is the root workspace
    """

    id: UUID
    folder_id: UUID | None
    title: str
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    """
    One message of a conversation: who said it and its content blocks, in
    the shape the Messages API takes them back
    """

    id: UUID
    role: Role
    content: list[dict[str, Any]]
    created_at: datetime


class ConversationWithMessages(Conversation):
    """
    A conversation and all its messages, in the order they were said
    """

    messages: list[Message]
