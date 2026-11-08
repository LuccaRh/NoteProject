# Imports
from collections.abc import AsyncIterator, Sequence
from typing import Any, cast
from uuid import UUID

from anthropic import APIError

from lonzo.core.connections import claude
from lonzo.schemas.conversations import Conversation, Message, Turn
from lonzo.schemas.settings import ModelSettings
from lonzo.services.conversations import (
    get_conversation,
    save_exchange,
    start_conversation,
)
from lonzo.services.note_tools import NoteTools
from lonzo.services.settings import get_model_settings
from lonzo.services.workspaces import base_rules, question_context


# Global variables
Event = tuple[str, dict[str, object]]


# Code
def blocks_of(content: Sequence[Any]) -> list[dict[str, Any]]:
    """
    The blocks of a turn of the model, only with what the API takes back
    """

    blocks: list[dict[str, Any]] = []

    for block in content:

        if block.type == "text" and block.text:
            blocks.append({"type": "text", "text": block.text})

        if block.type == "tool_use":
            blocks.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )

    return blocks


async def events(
    settings: ModelSettings,
    conversation: Conversation,
    history: list[Message],
    question: str,
    context: str,
) -> AsyncIterator[Event]:
    """
    The events of one answer, as (name, data), while the model writes; the
    text of every turn goes out, between the calls to the tools, each sent
    when it starts and again with its whole input. The question and every
    turn are kept at the end, and an error of the API mid-answer becomes
    an error event, with nothing kept
    """

    yield ("message_start", {"conversation_id": str(conversation.id)})
    turns: list[Turn] = []
    usage = {"input_tokens": 0, "output_tokens": 0, "cached_tokens": 0}
    end: dict[str, object] = {"usage": usage}
    tools = NoteTools(folder_id=conversation.folder_id)
    runner = claude.stream_answer(
        settings=settings,
        system=[base_rules()],
        history=history,
        question=question,
        tools=tools.tools(),
        context=context,
    )

    try:
        async for stream in runner:
            # The text of a new turn starts a paragraph of its own
            gap = "\n\n" if turns else ""

            async for event in stream:

                if event.type == "text":
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
            usage["cached_tokens"] += final.usage.cache_read_input_tokens or 0
            end["model"] = final.model
            end["stop_reason"] = final.stop_reason
            blocks = blocks_of(content=final.content)

            # The API refuses an empty turn, on every next question too
            if blocks:
                turns.append(("assistant", blocks))

            # The runner keeps these results and goes on with them
            results = await runner.generate_tool_call_response()

            if results is not None:
                content = cast(list[dict[str, Any]], results["content"])
                turns.append(("user", content))

    except APIError as error:
        yield ("error", {"message": error.message})

        return

    await save_exchange(
        conversation_id=conversation.id,
        question=question,
        turns=turns,
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

    settings = await get_model_settings()
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

    context = await question_context(folder_id=folder_id)

    return events(
        settings=settings,
        conversation=conversation,
        history=history,
        question=question,
        context=context,
    )
