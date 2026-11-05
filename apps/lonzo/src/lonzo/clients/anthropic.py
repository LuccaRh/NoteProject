# Imports
from typing import Any, cast

from anthropic import AsyncAnthropic
from anthropic.lib.tools import (
    BetaAsyncFunctionTool,
    BetaAsyncStreamingToolRunner,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaMessageParam,
    BetaTextBlockParam,
)

from lonzo.errors import MissingApiKey
from lonzo.schemas.conversations import Message


# Global variables
MODEL = "claude-haiku-5-5"
CHAT_MAX_TOKENS = 64000
TOOLS_MAX_TOKENS = 16000
TOOLS_MAX_TURNS = 20
CACHE: BetaCacheControlEphemeralParam = {"type": "ephemeral"}


# Code
class AnthropicClient:
    """
    The Anthropic API: one method per kind of call lonzo makes, with the
    model and limits fixed here
    """

    sdk: AsyncAnthropic

    def __init__(self) -> None:
        """
        One SDK client for the whole service, with the key of the
        environment, until there is a login
        """

        self.sdk = AsyncAnthropic()

    async def close(self) -> None:
        """
        Closes the connections kept open to the API
        """

        await self.sdk.close()

    def check_key(self) -> None:
        """
        MissingApiKey when the service has no key, before any call
        """

        if self.sdk.api_key is None:
            raise MissingApiKey("ANTHROPIC_API_KEY is not set")

    def stream_answer(
        self,
        system: list[str],
        history: list[Message],
        question: str,
        tools: list[BetaAsyncFunctionTool[Any]],
    ) -> BetaAsyncStreamingToolRunner[None]:
        """
        The answer to one question after the messages of the conversation,
        by the tool runner of the SDK: one stream per turn of the model,
        until it stops calling tools or reaches TOOLS_MAX_TURNS; the first
        piece of system is the fixed one, marked for the cache
        """

        self.check_key()
        # The blocks were saved in the shape the API takes them back
        messages = [
            cast(BetaMessageParam, {"role": m.role, "content": m.content})
            for m in history
        ]
        messages.append({"role": "user", "content": question})
        blocks: list[BetaTextBlockParam] = [
            {"type": "text", "text": text} for text in system if text
        ]
        blocks[0]["cache_control"] = CACHE

        return self.sdk.beta.messages.tool_runner(
            model=MODEL,
            max_tokens=CHAT_MAX_TOKENS,
            thinking={"type": "disabled"},
            system=blocks,
            messages=messages,
            tools=tools,
            max_iterations=TOOLS_MAX_TURNS,
            stream=True,
        )

    async def run_tools(
        self,
        system: str,
        request: str,
        tools: list[BetaAsyncFunctionTool[Any]],
    ) -> None:
        """
        The tool loop, run by the tool runner of the SDK: the model calls
        the tools until it stops or reaches TOOLS_MAX_TURNS
        """

        self.check_key()
        runner = self.sdk.beta.messages.tool_runner(
            model=MODEL,
            max_tokens=TOOLS_MAX_TOKENS,
            thinking={"type": "disabled"},
            system=system,
            messages=[{"role": "user", "content": request}],
            tools=tools,
            max_iterations=TOOLS_MAX_TURNS,
        )
        await runner.until_done()
