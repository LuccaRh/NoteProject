# Imports
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated

from anthropic import APIError, AsyncAnthropic
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lonzo.clients.anthropic import get_client, stream_answer


# Global variables
router = APIRouter(prefix="/chat")
RULES_PATH = Path(__file__).parent.parent / "rules.md"


# Code
class ChatRequest(BaseModel):
    question: str


# One server-sent event: a name and a JSON payload
def event(name: str, data: dict[str, object]) -> str:

    return f"event: {name}\ndata: {json.dumps(data)}\n\n"


# Events of one answer, sent to the client while the model writes
async def answer(question: str, client: AsyncAnthropic) -> AsyncIterator[str]:

    system = RULES_PATH.read_text(encoding="utf-8")
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
) -> StreamingResponse:

    return StreamingResponse(
        answer(question=body.question, client=client),
        media_type="text/event-stream",
    )
