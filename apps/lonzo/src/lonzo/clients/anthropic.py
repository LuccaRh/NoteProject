# Imports
from typing import Any, cast, get_args

from anthropic import AsyncAnthropic, AuthenticationError
from anthropic.lib.tools import (
    BetaAsyncFunctionTool,
    BetaAsyncStreamingToolRunner,
)
from anthropic.types import ModelInfo
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaThinkingConfigParam,
)

from lonzo.core.errors import InvalidApiKey
from lonzo.schemas.conversations import Message
from lonzo.schemas.settings import ModelOption, ModelSettings, Thinking


# Global variables
CACHE: BetaCacheControlEphemeralParam = {"type": "ephemeral"}


# Code
def thinking_of(model: ModelInfo) -> list[Thinking]:
    """
    The kinds of thinking the API says the model takes; none when it does
    not say
    """

    if model.capabilities is None:
        return []

    types = model.capabilities.thinking.types

    return [
        kind for kind in get_args(Thinking)
        if getattr(types, kind).supported
    ]


def thinking_config(kind: Thinking) -> BetaThinkingConfigParam:
    """
    The thinking of a call, in the shape the API takes it
    """

    return cast(BetaThinkingConfigParam, {"type": kind})


class AnthropicClient:
    """
    The Anthropic API: one method per kind of call lonzo makes, with the
    key, model and limit of the user
    """

    sdk: AsyncAnthropic

    def __init__(self) -> None:
        """
        One SDK client for the whole service, without a key; each call
        copies it with the key of the user
        """

        self.sdk = AsyncAnthropic()

    async def close(self) -> None:
        """
        Closes the connections kept open to the API
        """

        await self.sdk.close()

    async def list_models(self, api_key: str) -> list[ModelOption]:
        """
        The models that key can use; InvalidApiKey when the API refuses it
        """

        sdk = self.sdk.with_options(api_key=api_key)

        try:
            return [
                ModelOption(
                    id=model.id,
                    name=model.display_name,
                    max_tokens=model.max_tokens,
                    thinking=thinking_of(model=model),
                )
                async for model in sdk.models.list()
            ]
        except AuthenticationError as error:
            raise InvalidApiKey("the Anthropic key was refused") from error

    def stream_answer(
        self,
        settings: ModelSettings,
        system: list[str],
        history: list[Message],
        question: str,
        tools: list[BetaAsyncFunctionTool[Any]],
    ) -> BetaAsyncStreamingToolRunner[None]:
        """
        The answer to one question after the messages of the conversation,
        by the tool runner of the SDK: one stream per turn of the model,
        until it stops calling tools or reaches the turns of the user; the
        first piece of system is the fixed one, marked for the cache
        """

        sdk = self.sdk.with_options(api_key=settings.api_key)
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

        return sdk.beta.messages.tool_runner(
            model=settings.model,
            max_tokens=settings.max_tokens,
            thinking=thinking_config(kind=settings.thinking),
            system=blocks,
            messages=messages,
            tools=tools,
            max_iterations=settings.tools_max_turns,
            cache_control=CACHE,
            stream=True,
        )

    async def run_tools(
        self,
        settings: ModelSettings,
        system: str,
        request: str,
        tools: list[BetaAsyncFunctionTool[Any]],
    ) -> None:
        """
        The tool loop, run by the tool runner of the SDK: the model calls
        the tools until it stops or reaches the turns of the user, in at
        most their tokens per turn
        """

        sdk = self.sdk.with_options(api_key=settings.api_key)
        runner = sdk.beta.messages.tool_runner(
            model=settings.model,
            max_tokens=settings.max_tokens,
            thinking=thinking_config(kind=settings.thinking),
            system=system,
            messages=[{"role": "user", "content": request}],
            tools=tools,
            max_iterations=settings.tools_max_turns,
            cache_control=CACHE,
        )
        await runner.until_done()
