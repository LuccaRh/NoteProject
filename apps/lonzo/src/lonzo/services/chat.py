# Imports
from collections.abc import AsyncIterator
from uuid import UUID

from anthropic import APIError

from lonzo.connections import claude
from lonzo.schemas.conversations import Conversation, Message
from lonzo.services.conversations import (
    get_conversation,
    save_exchange,
    start_conversation,
)
from lonzo.services.workspaces import workspace_rules


# Global variables
Event = tuple[str, dict[str, object]]


# Code
async def events(
    conversation: Conversation,
    history: list[Message],
    question: str,
    system: str,
) -> AsyncIterator[Event]:
    """
    The events of one answer, as (name, data), while the model writes; the
    question and the whole answer are kept at the end, and an error of the
    API mid-answer becomes an error event, with nothing kept
    """

    yield ("message_start", {"conversation_id": str(conversation.id)})
    chunks: list[str] = []

    try:
        async with claude.stream_answer(
            system=system,
            history=history,
            question=question,
        ) as stream:
            async for text in stream.text_stream:
                chunks.append(text)
                yield ("text_delta", {"text": text})

            final = await stream.get_final_message()

    except APIError as error:
        yield ("error", {"message": error.message})

        return

    await save_exchange(
        conversation_id=conversation.id,
        question=question,
        answer="".join(chunks),
    )
    usage = {
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
    }
    end: dict[str, object] = {
        "model": final.model,
        "stop_reason": final.stop_reason,
        "usage": usage,
    }
    yield ("message_end", end)


async def answer(
    question: str,
    folder_id: UUID | None,
    conversation_id: UUID | None,
) -> AsyncIterator[Event]:
    """
    Starts the answer to a question: in a new conversation of the folder's
    workspace, or after the messages of conversation_id (whose workspace
    wins over folder_id). The key, the conversation and the rules are
    checked before the first event, so their errors still become a status
    code
    """

    claude.check_key()
    conversation: Conversation | None = None
    history: list[Message] = []

    if conversation_id is not None:
        conversation = await get_conversation(conversation_id=conversation_id)
        folder_id = conversation.folder_id
        history = conversation.messages

    if conversation is None:
        conversation = await start_conversation(
            folder_id=folder_id,
            question=question,
        )

    system = await workspace_rules(folder_id=folder_id)

    return events(
        conversation=conversation,
        history=history,
        question=question,
        system=system,
    )
