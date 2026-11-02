# Imports
import os
from datetime import date
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic, omit
from anthropic.lib.streaming import AsyncMessageStreamManager
from anthropic.lib.tools import BetaAsyncFunctionTool
from fastapi import HTTPException


# Global variables
MODEL = "claude-haiku-5-5"
CHAT_MAX_TOKENS = 512
WORKSPACE_MAX_TOKENS = 16000
WORKSPACE_MAX_TURNS = 20
PROMPT_PATH = Path(__file__).parent.parent / "create_workspace.md"


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
        system=system or omit,
        messages=[{"role": "user", "content": question}],
    )


async def write_workspace(
    client: AsyncAnthropic,
    description: str,
    tools: list[BetaAsyncFunctionTool[Any]],
) -> None:
    """
    The tool loop, run by the tool runner of the SDK: from the person's
    text, the model saves the workspace one note per tool call, until it
    stops calling tools or reaches WORKSPACE_MAX_TURNS
    """

    # The prompt never changes, so the system prompt stays the same for
    # the cache; the date goes with the text
    system = PROMPT_PATH.read_text(encoding="utf-8")
    request = f"Today is {date.today().isoformat()}.\n\n{description}"
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=WORKSPACE_MAX_TOKENS,
        thinking={"type": "disabled"},
        system=system,
        messages=[{"role": "user", "content": request}],
        tools=tools,
        max_iterations=WORKSPACE_MAX_TURNS,
    )
    await runner.until_done()
