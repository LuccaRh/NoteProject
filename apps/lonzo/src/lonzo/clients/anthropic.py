# Imports
from typing import Any

from anthropic import AsyncAnthropic, omit
from anthropic.lib.streaming import AsyncMessageStreamManager
from anthropic.lib.tools import BetaAsyncFunctionTool

from lonzo.errors import MissingApiKey


# Global variables
MODEL = "claude-haiku-5-5"
CHAT_MAX_TOKENS = 512
TOOLS_MAX_TOKENS = 16000
TOOLS_MAX_TURNS = 20


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
        system: str,
        question: str,
    ) -> AsyncMessageStreamManager[None]:
        """
        The answer to one question, streamed while the model writes; an
        empty system goes as no system prompt
        """

        self.check_key()

        return self.sdk.messages.stream(
            model=MODEL,
            max_tokens=CHAT_MAX_TOKENS,
            thinking={"type": "disabled"},
            system=system or omit,
            messages=[{"role": "user", "content": question}],
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
