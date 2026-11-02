# Imports
import json
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lonzo.services.chat import Event, answer


# Global variables
router = APIRouter(prefix="/chat")


# Code
class ChatRequest(BaseModel):
    """
    A question and, optionally, the workspace folder it is asked in
    """

    question: str
    folder_id: UUID | None = None


async def server_sent(events: AsyncIterator[Event]) -> AsyncIterator[str]:
    """
    Each event as one server-sent event: a name and a JSON payload
    """

    async for name, data in events:
        yield f"event: {name}\ndata: {json.dumps(data)}\n\n"


@router.post("")
async def post_chat(body: ChatRequest) -> StreamingResponse:
    """
    Answers a question in server-sent events, with the rules of the
    root and folder workspaces; without any, with no rules
    """

    events = await answer(question=body.question, folder_id=body.folder_id)

    return StreamingResponse(
        server_sent(events=events),
        media_type="text/event-stream",
    )
