# Imports
import os

from anthropic import AsyncAnthropic
from anthropic.lib.streaming import AsyncMessageStreamManager
from fastapi import HTTPException


# Global variables
MODEL = "claude-haiku-5-5"
CHAT_MAX_TOKENS = 512


# Code
def get_client() -> AsyncAnthropic:
    """
    Client of the Anthropic API, with one key for the whole service until
    there is a login
    """

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "ANTHROPIC_API_KEY is not set")

    return AsyncAnthropic()


def stream_answer(
    client: AsyncAnthropic,
    system: str,
    question: str,
) -> AsyncMessageStreamManager[None]:
    """
    The answer to one question, streamed while the model writes; without
    workspace rules the call goes with no system prompt
    """

    return client.messages.stream(
        model=MODEL,
        max_tokens=CHAT_MAX_TOKENS,
        thinking={"type": "disabled"},
        system=system,
        messages=[{"role": "user", "content": question}],
    )
