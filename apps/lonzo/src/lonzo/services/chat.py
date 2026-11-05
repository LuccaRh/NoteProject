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
from lonzo.services.note_tools import NoteTools
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
    text of every turn goes out, between the calls to the tools, each sent
    when it starts and again with its whole input. The question and the
    whole answer are kept at the end, and an error of the API mid-answer
    becomes an error event, with nothing kept
    """

    yield ("message_start", {"conversation_id": str(conversation.id)})
    chunks: list[str] = []
    usage = {"input_tokens": 0, "output_tokens": 0}
    end: dict[str, object] = {"usage": usage}
    tools = NoteTools()
    runner = claude.stream_answer(
        system=system,
        history=history,
        question=question,
        tools=tools.tools(),
    )

    try:
        async for stream in runner:
            # The text of a new turn starts a paragraph of its own
            gap = "\n\n" if chunks else ""

            async for event in stream:

                if event.type == "text":
                    chunks.append(gap + event.text)
                    yield ("text_delta", {"text": gap + event.text})
                    gap = ""

                if (
                    event.type == "content_block_start"
                    or event.type == "content_block_stop"
                ):
                    block = event.content_block

                    if block.type == "tool_use":
                        target = tools.target(tool_input=block.input)
                        yield (
                            "tool_use",
                            {"name": block.name, "target": target},
                        )

            final = await stream.get_final_message()
            usage["input_tokens"] += final.usage.input_tokens
            usage["output_tokens"] += final.usage.output_tokens
            end["model"] = final.model
            end["stop_reason"] = final.stop_reason

    except APIError as error:
        yield ("error", {"message": error.message})

        return

    await save_exchange(
        conversation_id=conversation.id,
        question=question,
        answer="".join(chunks),
    )
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
