# Imports
import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from types import SimpleNamespace
from typing import Any, ClassVar
from unittest.mock import patch
from uuid import UUID, uuid4

import httpx2
import pytest
from fakes import USER, FakeIchiro, unreachable
from fastapi.testclient import TestClient
from httpx2 import Response

from lonzo import connections
from lonzo.main import app
from lonzo.services.conversations import get_conversation
from lonzo.services.workspaces import base_rules
from lonzo.user import current_user


# Global variables
pytestmark = pytest.mark.usefixtures("saved_key")
client = TestClient(app, headers={"X-User-Id": str(USER)})


# Code
# Stands in for the stream of the anthropic client: before, then two chunks
class FakeStream:
    before: ClassVar[list[SimpleNamespace]] = []
    content: ClassVar[list[SimpleNamespace]] = [
        SimpleNamespace(type="text", text="Hello there"),
    ]

    async def __aiter__(self) -> AsyncIterator[SimpleNamespace]:

        for event in FakeStream.before:
            yield event

        for text in ("Hello", " there"):
            yield SimpleNamespace(type="text", text=text)

    async def get_final_message(self) -> SimpleNamespace:

        usage = SimpleNamespace(
            input_tokens=10,
            output_tokens=2,
            cache_read_input_tokens=7,
        )

        return SimpleNamespace(
            model="claude-haiku-5-5",
            stop_reason="end_turn",
            usage=usage,
            content=FakeStream.content,
        )


# Stands in for the tool runner: one stream per turn of the model
class FakeRunner:
    turns: ClassVar[int] = 1
    results: ClassVar[dict[str, Any] | None] = None

    async def __aiter__(self) -> AsyncIterator[FakeStream]:

        for _ in range(FakeRunner.turns):
            yield FakeStream()

    async def generate_tool_call_response(self) -> dict[str, Any] | None:

        return FakeRunner.results


# Keeps the parameters of the last call, to check the system prompt
class FakeMessages:
    params: ClassVar[dict[str, object]] = {}

    def tool_runner(self, **params: object) -> FakeRunner:

        FakeMessages.params = params

        return FakeRunner()


class FakeClient:
    used_key: ClassVar[str] = ""
    beta: SimpleNamespace = SimpleNamespace(messages=FakeMessages())

    def with_options(self, api_key: str) -> FakeClient:

        FakeClient.used_key = api_key

        return self


# Parses a server-sent events body into (name, data) pairs
def parse(body: str) -> list[tuple[str, dict[str, object]]]:

    events = []

    for block in body.strip().split("\n\n"):
        name, data = block.split("\n")
        events.append((name.removeprefix("event: "),
                       json.loads(data.removeprefix("data: "))))

    return events


def post(
    body: Mapping[str, object],
    http: httpx2.AsyncClient | None = None,
) -> Response:

    http = http or FakeIchiro().client()

    with (
        patch.object(connections.claude, "sdk", FakeClient()),
        patch.object(connections.ichiro, "http", http),
    ):
        return client.post("/chat", json=body)


def test_chat_streams_named_events() -> None:

    response = post(body={"question": "Hi"})

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

    response = post(body={})

    assert response.status_code == 422


def test_chat_without_key() -> None:

    client.delete("/chat/settings/key")

    response = post(body={"question": "Hi"})

    assert response.status_code == 422
    assert "settings" in response.json()["detail"]


def test_chat_with_notes_service_down() -> None:

    body = {"question": "Hi", "folder_id": str(uuid4())}
    response = post(body=body, http=unreachable())

    assert response.status_code == 502


def test_chat_without_workspace_has_only_the_base_rules() -> None:

    post(body={"question": "Hi"})

    system = FakeMessages.params["system"]
    assert isinstance(system, list)
    assert system[0]["text"] == base_rules()
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    assert system[1]["text"].endswith("Current folder: /")


def test_chat_uses_the_folder_workspace_rules() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    workspace = ichiro.add(title=".workspace", parent_id=folder, is_folder=True)
    ichiro.add(title="Fixed facts", parent_id=workspace, body="Bats left.")
    other = ichiro.add(title="Calculus", is_folder=True)
    elsewhere = ichiro.add(title=".workspace", parent_id=other, is_folder=True)
    ichiro.add(title="Fixed facts", parent_id=elsewhere, body="Exam soon.")

    body = {"question": "Hi", "folder_id": str(folder)}
    post(body=body, http=ichiro.client())

    system = FakeMessages.params["system"]
    assert isinstance(system, list)
    assert system[-1]["text"].endswith("# Fixed facts\n\nBats left.")
    assert "Exam soon." not in str(system)


def test_chat_lists_the_skills_without_their_bodies() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    workspace = ichiro.add(title=".workspace", parent_id=folder, is_folder=True)
    skills = ichiro.add(title="skills", parent_id=workspace, is_folder=True)
    skill = ichiro.add(
        title="review-swing",
        parent_id=skills,
        body="Reviews a swing.\nLook at the video twice.",
    )

    body = {"question": "Hi", "folder_id": str(folder)}
    post(body=body, http=ichiro.client())

    system = str(FakeMessages.params["system"])
    assert f"- {skill} review-swing: Reviews a swing." in system
    assert "Look at the video" not in system


def test_chat_names_the_folder_by_its_whole_path() -> None:

    ichiro = FakeIchiro()
    sport = ichiro.add(title="Sport", is_folder=True)
    folder = ichiro.add(title="Baseball", parent_id=sport, is_folder=True)

    body = {"question": "Hi", "folder_id": str(folder)}
    post(body=body, http=ichiro.client())

    assert "Current folder: /Sport/Baseball" in str(
        FakeMessages.params["system"]
    )


def test_chat_marks_the_messages_for_the_cache() -> None:

    post(body={"question": "Hi"})

    assert FakeMessages.params["cache_control"] == {"type": "ephemeral"}


def test_chat_gives_the_model_the_note_tools() -> None:

    post(body={"question": "Hi"})

    tools = FakeMessages.params["tools"]
    assert isinstance(tools, list)
    assert {tool.name for tool in tools} == {
        "search_notes",
        "search_titles",
        "list_folder",
        "read_note",
        "create_note",
        "create_folder",
        "edit_note",
        "delete_note",
    }


def test_chat_streams_the_text_of_every_turn() -> None:

    with patch.object(FakeRunner, "turns", 2):
        response = post(body={"question": "Hi"})

    events = parse(body=response.text)
    text = "".join(str(data["text"]) for name, data in events
                   if name == "text_delta")
    assert text == "Hello there\n\nHello there"
    assert events[-1][1]["usage"] == {
        "input_tokens": 20,
        "output_tokens": 4,
        "cached_tokens": 14,
    }


def tool_event(kind: str, tool_input: dict[str, object]) -> SimpleNamespace:

    block = SimpleNamespace(
        type="tool_use",
        name="create_note",
        input=tool_input,
    )

    return SimpleNamespace(type=kind, content_block=block)


def test_chat_streams_the_tool_calls() -> None:

    start = tool_event(kind="content_block_start", tool_input={})
    stop = tool_event(
        kind="content_block_stop",
        tool_input={"path": "Games/Chess", "body": "Long body"},
    )

    with patch.object(FakeStream, "before", [start, stop]):
        response = post(body={"question": "Hi"})

    tools = [data for name, data in parse(body=response.text)
             if name == "tool_use"]
    assert tools == [
        {"name": "create_note", "target": None},
        {"name": "create_note", "target": "Chess"},
    ]


def test_chat_ignores_blocks_that_are_not_tools() -> None:

    block = SimpleNamespace(type="text")
    start = SimpleNamespace(type="content_block_start", content_block=block)

    with patch.object(FakeStream, "before", [start]):
        response = post(body={"question": "Hi"})

    assert "tool_use" not in [name for name, _ in parse(body=response.text)]


def conversation_of(response: Response) -> str:

    start = parse(body=response.text)[0]

    assert start[0] == "message_start"

    return str(start[1]["conversation_id"])


def test_chat_keeps_the_question_and_answer() -> None:

    response = post(body={"question": "Who bats left?"})
    conversation_id = conversation_of(response=response)

    # Outside a request: the service reads as the user of the chat
    token = current_user.set(USER)
    found = asyncio.run(get_conversation(conversation_id=UUID(conversation_id)))
    current_user.reset(token)

    assert found.title == "Who bats left?"
    assert [(m.role, m.content) for m in found.messages] == [
        ("user", [{"type": "text", "text": "Who bats left?"}]),
        ("assistant", [{"type": "text", "text": "Hello there"}]),
    ]


def test_chat_keeps_the_tool_calls_of_an_answer() -> None:

    call = SimpleNamespace(
        type="tool_use",
        id="toolu_1",
        name="read_note",
        input={"note_id": "1"},
    )
    result = {"type": "tool_result", "tool_use_id": "toolu_1", "content": "Hi"}
    results = {"role": "user", "content": [result]}

    with (
        patch.object(FakeStream, "content", [call]),
        patch.object(FakeRunner, "results", results),
    ):
        response = post(body={"question": "Read it"})

    conversation_id = conversation_of(response=response)
    second = post(
        body={"question": "And now?", "conversation_id": conversation_id},
    )

    assert second.status_code == 200
    messages = FakeMessages.params["messages"]
    assert isinstance(messages, list)
    assert [m["role"] for m in messages] == [
        "user",
        "assistant",
        "user",
        "user",
    ]
    assert messages[1]["content"] == [
        {
            "type": "tool_use",
            "id": "toolu_1",
            "name": "read_note",
            "input": {"note_id": "1"},
        }
    ]
    assert messages[2]["content"] == [result]


def test_chat_sends_the_history_of_the_conversation() -> None:

    first = post(body={"question": "Who bats left?"})
    conversation_id = conversation_of(response=first)

    second = post(
        body={"question": "And right?", "conversation_id": conversation_id},
    )

    assert conversation_of(response=second) == conversation_id
    question = [{"type": "text", "text": "Who bats left?"}]
    answer = [{"type": "text", "text": "Hello there"}]
    assert FakeMessages.params["messages"] == [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
        {"role": "user", "content": "And right?"},
    ]


def test_chat_in_a_missing_conversation() -> None:

    body = {"question": "Hi", "conversation_id": str(uuid4())}
    response = post(body=body)

    assert response.status_code == 404


def test_chat_keeps_no_empty_turn() -> None:

    empty = SimpleNamespace(type="text", text="")

    with patch.object(FakeStream, "content", [empty]):
        response = post(body={"question": "Hi"})

    conversation_id = conversation_of(response=response)
    post(body={"question": "Still there?", "conversation_id": conversation_id})

    messages = FakeMessages.params["messages"]
    assert isinstance(messages, list)
    assert [m["role"] for m in messages] == ["user", "user"]
