# Imports
import json
from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

import httpx2
from anthropic import APIError, AsyncAnthropic
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lonzo.clients.anthropic import get_client, stream_answer
from lonzo.clients.ichiro import get_ichiro, workspace_rules


# Global variables
router = APIRouter(prefix="/chat")


# Code
class ChatRequest(BaseModel):
    """
    A question and, optionally, the workspace folder it is asked in
    """

    question: str
    folder_id: UUID | None = None


def event(name: str, data: dict[str, object]) -> str:
    """
    One server-sent event: a name and a JSON payload
    """

    return f"event: {name}\ndata: {json.dumps(data)}\n\n"


async def answer(
    question: str,
    system: str,
    client: AsyncAnthropic,
) -> AsyncIterator[str]:
    """
    Events of one answer, sent to the client while the model writes
    """

    yield event(name="message_start", data={})

    try:
        async with stream_answer(
            client=client,
            system=system,
            question=question,
        ) as stream:
            async for text in stream.text_stream:
                yield event(name="text_delta", data={"text": text})

            final = await stream.get_final_message()

    except APIError as error:
        yield event(name="error", data={"message": error.message})

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
    yield event(name="message_end", data=end)


@router.post("")
async def chat(
    body: ChatRequest,
    client: Annotated[AsyncAnthropic, Depends(get_client)],
    ichiro: Annotated[httpx2.AsyncClient, Depends(get_ichiro)],
) -> StreamingResponse:
    """
    Answers a question in server-sent events, with the rules of the
    root and folder workspaces; without any, with no rules
    """

    # Read before the stream starts: an ichiro error is still a status code
    system = await workspace_rules(ichiro=ichiro, folder_id=body.folder_id)

    return StreamingResponse(
        answer(question=body.question, system=system, client=client),
        media_type="text/event-stream",
    )
