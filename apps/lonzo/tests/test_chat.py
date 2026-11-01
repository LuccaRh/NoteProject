# Imports
import json
from collections.abc import AsyncIterator
from types import SimpleNamespace, TracebackType
from typing import Self

import pytest
from fastapi.testclient import TestClient

from lonzo.main import app
from lonzo.routers.chat import get_client


# Global variables
client = TestClient(app)


# Code
# Stands in for the stream of the anthropic client: two chunks of text
class FakeStream:

    async def __aenter__(self) -> Self:

        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:

        return None

    @property
    async def text_stream(self) -> AsyncIterator[str]:

        for text in ("Hello", " there"):
            yield text

    async def get_final_message(self) -> SimpleNamespace:

        usage = SimpleNamespace(input_tokens=10, output_tokens=2)

        return SimpleNamespace(stop_reason="end_turn", usage=usage)


class FakeMessages:

    def stream(self, **params: object) -> FakeStream:

        return FakeStream()


class FakeClient:
    messages: FakeMessages = FakeMessages()


# Parses a server-sent events body into (name, data) pairs
def parse(body: str) -> list[tuple[str, dict[str, object]]]:

    events = []

    for block in body.strip().split("\n\n"):
        name, data = block.split("\n")
        events.append((name.removeprefix("event: "),
                       json.loads(data.removeprefix("data: "))))

    return events


def test_chat_streams_named_events() -> None:

    app.dependency_overrides[get_client] = FakeClient
    response = client.post("/chat", json={"question": "Hi"})
    app.dependency_overrides.clear()

    assert response.headers["content-type"].startswith("text/event-stream")
    events = parse(response.text)
    assert [name for name, _ in events] == [
        "message_start", "text_delta", "text_delta", "message_end"
    ]
    text = "".join(str(data["text"]) for name, data in events
                   if name == "text_delta")
    assert text == "Hello there"
    assert events[-1][1]["stop_reason"] == "end_turn"


def test_chat_needs_a_question() -> None:

    app.dependency_overrides[get_client] = FakeClient
    response = client.post("/chat", json={})
    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_chat_without_key(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post("/chat", json={"question": "Hi"})

    assert response.status_code == 503
