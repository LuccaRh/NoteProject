# Imports
from collections.abc import AsyncIterator
from uuid import UUID

from anthropic import APIError

from lonzo.connections import claude
from lonzo.services.workspaces import workspace_rules


# Global variables
Event = tuple[str, dict[str, object]]


# Code
async def events(question: str, system: str) -> AsyncIterator[Event]:
    """
    The events of one answer, as (name, data), while the model writes; an
    error of the API mid-answer becomes an error event
    """

    yield ("message_start", {})

    try:
        async with claude.stream_answer(
            system=system,
            question=question,
        ) as stream:
            async for text in stream.text_stream:
                yield ("text_delta", {"text": text})

            final = await stream.get_final_message()

    except APIError as error:
        yield ("error", {"message": error.message})

        return

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


async def answer(question: str, folder_id: UUID | None) -> AsyncIterator[Event]:
    """
    Starts the answer to a question with the rules of the root and folder
    workspaces; the key and the rules are checked before the first event,
    so their errors still become a status code
    """

    claude.check_key()
    system = await workspace_rules(folder_id=folder_id)

    return events(question=question, system=system)
