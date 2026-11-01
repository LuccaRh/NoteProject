# Imports
import json
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated

from anthropic import APIError, AsyncAnthropic
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# Global variables
router = APIRouter(prefix="/chat")
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 512
RULES_PATH = Path(__file__).parent.parent / "rules.md"


# Code
class ChatRequest(BaseModel):
    question: str


# One key for the whole service until there is a login
def get_client() -> AsyncAnthropic:

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "ANTHROPIC_API_KEY is not set")

    return AsyncAnthropic()


# One server-sent event: a name and a JSON payload
def event(name: str, data: dict[str, object]) -> str:

    return f"event: {name}\ndata: {json.dumps(data)}\n\n"


# Events of one answer, sent to the client while the model writes
async def answer(question: str, client: AsyncAnthropic) -> AsyncIterator[str]:

    yield event("message_start", {"model": MODEL})

    try:
        async with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "disabled"},
            system=RULES_PATH.read_text(encoding="utf-8"),
            messages=[{"role": "user", "content": question}],
        ) as stream:
            async for text in stream.text_stream:
                yield event("text_delta", {"text": text})

            final = await stream.get_final_message()

    except APIError as error:
        yield event("error", {"message": error.message})

        return

    usage = {
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
    }
    yield event(
        "message_end", {"stop_reason": final.stop_reason, "usage": usage}
    )


@router.post("")
async def chat(
    body: ChatRequest,
    client: Annotated[AsyncAnthropic, Depends(get_client)],
) -> StreamingResponse:

    return StreamingResponse(
        answer(body.question, client), media_type="text/event-stream"
    )
