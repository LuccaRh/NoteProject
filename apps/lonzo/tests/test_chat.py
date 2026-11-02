# Imports
import json
from collections.abc import AsyncIterator
from types import SimpleNamespace, TracebackType
from typing import ClassVar, Self

import pytest
from anthropic import omit
from fakes import FakeIchiro, unreachable
from fastapi.testclient import TestClient

from lonzo.clients.anthropic import get_client
from lonzo.clients.ichiro import get_ichiro
from lonzo.main import app


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

        return SimpleNamespace(
            model="claude-haiku-5-5",
            stop_reason="end_turn",
            usage=usage,
        )


# Keeps the parameters of the last call, to check the system prompt
class FakeMessages:
    params: ClassVar[dict[str, object]] = {}

    def stream(self, **params: object) -> FakeStream:

        FakeMessages.params = params

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
    app.dependency_overrides[get_ichiro] = FakeIchiro().client
    response = client.post("/chat", json={"question": "Hi"})
    app.dependency_overrides.clear()

    assert response.headers["content-type"].startswith("text/event-stream")
    events = parse(body=response.text)
    assert [name for name, _ in events] == [
        "message_start", "text_delta", "text_delta", "message_end"
    ]
    text = "".join(str(data["text"]) for name, data in events
                   if name == "text_delta")
    assert text == "Hello there"
    assert events[-1][1]["stop_reason"] == "end_turn"


def test_chat_needs_a_question() -> None:

    app.dependency_overrides[get_client] = FakeClient
    app.dependency_overrides[get_ichiro] = FakeIchiro().client
    response = client.post("/chat", json={})
    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_chat_without_key(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post("/chat", json={"question": "Hi"})

    assert response.status_code == 503


def test_chat_with_notes_service_down() -> None:

    app.dependency_overrides[get_client] = FakeClient
    app.dependency_overrides[get_ichiro] = unreachable
    response = client.post("/chat", json={"question": "Hi"})
    app.dependency_overrides.clear()

    assert response.status_code == 502


def test_chat_without_workspace_has_no_rules() -> None:

    app.dependency_overrides[get_client] = FakeClient
    app.dependency_overrides[get_ichiro] = FakeIchiro().client
    client.post("/chat", json={"question": "Hi"})
    app.dependency_overrides.clear()

    assert FakeMessages.params["system"] is omit


def test_chat_uses_root_and_folder_workspace_rules() -> None:

    ichiro = FakeIchiro()
    root = ichiro.add(title=".workspace", is_folder=True)
    ichiro.add(title="How to answer", parent_id=root, body="Be short.")
    folder = ichiro.add(title="Baseball", is_folder=True)
    workspace = ichiro.add(title=".workspace", parent_id=folder, is_folder=True)
    ichiro.add(title="Fixed facts", parent_id=workspace, body="Bats left.")
    other = ichiro.add(title="Calculus", is_folder=True)
    elsewhere = ichiro.add(title=".workspace", parent_id=other, is_folder=True)
    ichiro.add(title="Fixed facts", parent_id=elsewhere, body="Exam soon.")

    app.dependency_overrides[get_client] = FakeClient
    app.dependency_overrides[get_ichiro] = ichiro.client
    body = {"question": "Hi", "folder_id": str(folder)}
    client.post("/chat", json=body)
    app.dependency_overrides.clear()

    system = str(FakeMessages.params["system"])
    assert system.endswith(
        "# How to answer\n\nBe short.\n\n# Fixed facts\n\nBats left."
    )
    assert "Exam soon." not in system
