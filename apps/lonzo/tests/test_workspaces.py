# Imports
from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any, ClassVar
from unittest.mock import patch
from uuid import uuid4

from fakes import FakeIchiro
from fastapi.testclient import TestClient
from httpx2 import Response

from lonzo import connections
from lonzo.errors import TitleTaken
from lonzo.main import app


# Global variables
client = TestClient(app)


# Code
def call(name: str, **arguments: object) -> SimpleNamespace:

    return SimpleNamespace(
        type="tool_use",
        id=f"call-{name}",
        name=name,
        input=arguments,
    )


# Stands in for the tool runner: runs each turn of tool calls with the
# real tools, keeping what each answered; an error of a tool goes back
# to the model, as the SDK does with any exception
class FakeRunner:
    turns: ClassVar[list[list[SimpleNamespace]]] = []
    params: ClassVar[dict[str, Any]] = {}
    results: ClassVar[list[dict[str, object]]] = []

    def __init__(self, **params: Any) -> None:

        FakeRunner.params = params
        FakeRunner.results = []

    async def until_done(self) -> None:

        tools = {tool.name: tool for tool in FakeRunner.params["tools"]}

        for turn in FakeRunner.turns:
            for block in turn:
                try:
                    content = await tools[block.name].call(block.input)
                except (ValueError, TitleTaken) as error:
                    result = {"content": str(error), "is_error": True}
                else:
                    result = {"content": content, "is_error": False}

                FakeRunner.results.append({"id": block.id, **result})


class FakeClient:
    api_key: str = "test-key"
    messages: SimpleNamespace = SimpleNamespace(tool_runner=FakeRunner)
    beta: SimpleNamespace = SimpleNamespace(messages=messages)


def post(
    ichiro: FakeIchiro,
    body: Mapping[str, object],
    turns: list[list[SimpleNamespace]] | None = None,
) -> Response:

    FakeRunner.turns = turns or []

    with (
        patch.object(connections.claude, "sdk", FakeClient()),
        patch.object(connections.ichiro, "http", ichiro.client()),
    ):
        return client.post("/chat/workspaces", json=body)


def test_workspace_saves_rules_and_skills_in_the_folder() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    rules = call(
        name="create_note",
        path=".workspace/CLAUDE.md",
        body="# Workspace\n\nHit better.",
    )
    skill = call(
        name="create_note",
        path=".workspace/skills/review-swing",
        body="Look at the video.",
    )
    response = post(ichiro=ichiro, body=body, turns=[[rules], [skill]])

    assert response.status_code == 201
    workspace, kb, skills, scripts, hooks, rules, skill = response.json()
    assert workspace["title"] == ".workspace"
    assert workspace["is_folder"] is True
    assert workspace["parent_id"] == str(folder)
    assert rules["title"] == "CLAUDE.md"
    assert rules["parent_id"] == workspace["id"]
    assert rules["body"].endswith("Hit better.")
    assert [kb["title"], scripts["title"], hooks["title"]] == [
        "kb",
        "scripts",
        "hooks",
    ]
    assert skills["title"] == "skills"
    assert skills["is_folder"] is True
    assert skills["parent_id"] == workspace["id"]
    assert skill["title"] == "review-swing"
    assert skill["parent_id"] == skills["id"]


def test_note_creates_the_folders_on_its_path() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    rules = call(name="create_note", path=".workspace/CLAUDE.md", body="")
    note = call(name="create_note", path="Games/2026/first", body="Won.")
    response = post(ichiro=ichiro, body=body, turns=[[rules, note]])

    assert response.status_code == 201
    games, year, first = response.json()[-3:]
    assert games["title"] == "Games"
    assert games["parent_id"] == str(folder)
    assert year["title"] == "2026"
    assert year["parent_id"] == games["id"]
    assert first["title"] == "first"
    assert first["parent_id"] == year["id"]


def test_path_outside_the_folder_goes_back_as_an_error() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    wrong = call(name="create_note", path="../Other/x", body="")
    rules = call(name="create_note", path=".workspace/CLAUDE.md", body="")
    response = post(ichiro=ichiro, body=body, turns=[[wrong], [rules]])

    assert response.status_code == 201
    assert len(response.json()) == 6
    assert FakeRunner.results[0]["is_error"] is True


def test_taken_title_goes_back_as_an_error() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    again = call(name="create_folder", path=".workspace/kb")
    rules = call(name="create_note", path=".workspace/CLAUDE.md", body="")
    response = post(ichiro=ichiro, body=body, turns=[[again, rules]])

    assert response.status_code == 201
    assert FakeRunner.results[0]["content"] == "kb already exists"


def test_note_on_the_path_goes_back_as_an_error() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    ichiro.add(title="Games", parent_id=folder)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    note = call(name="create_note", path="Games/2026/first", body="Won.")
    rules = call(name="create_note", path=".workspace/CLAUDE.md", body="")
    response = post(ichiro=ichiro, body=body, turns=[[note, rules]])

    assert response.status_code == 201
    assert FakeRunner.results[0]["content"] == "Games is a note, not a folder"


def test_workspace_needs_a_folder_id() -> None:

    body = {"description": "I play baseball"}
    response = post(ichiro=FakeIchiro(), body=body)

    assert response.status_code == 422


def test_workspace_in_a_missing_folder() -> None:

    body = {"folder_id": str(uuid4()), "description": "I play baseball"}
    response = post(ichiro=FakeIchiro(), body=body)

    assert response.status_code == 404


def test_workspace_in_a_note() -> None:

    ichiro = FakeIchiro()
    note = ichiro.add(title="Shopping list")
    body = {"folder_id": str(note), "description": "I play baseball"}
    response = post(ichiro=ichiro, body=body)

    assert response.status_code == 422


def test_workspace_reuses_the_folders_already_there() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    workspace = ichiro.add(title=".workspace", parent_id=folder, is_folder=True)
    ichiro.add(title="kb", parent_id=workspace, is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}
    rules = call(name="create_note", path=".workspace/CLAUDE.md", body="")
    response = post(ichiro=ichiro, body=body, turns=[[rules]])

    assert response.status_code == 201
    titles = [note["title"] for note in response.json()]
    assert titles == ["skills", "scripts", "hooks", "CLAUDE.md"]
    assert len(ichiro.rows) == 7
