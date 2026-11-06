# Imports
import asyncio
from collections.abc import AsyncIterator, Mapping
from types import SimpleNamespace
from typing import ClassVar
from unittest.mock import patch

import httpx2
from anthropic import AuthenticationError
from fakes import OTHER_USER, USER, FakeIchiro
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import text
from test_chat import FakeClient, FakeMessages
from test_chat import post as ask
from test_workspaces import FakeRunner
from test_workspaces import post as create_workspace

from lonzo import connections, db
from lonzo.core.cipher import decrypt
from lonzo.main import app
from lonzo.user import current_user


# Global variables
client = TestClient(app, headers={"X-User-Id": str(USER)})
other_client = TestClient(app, headers={"X-User-Id": str(OTHER_USER)})
KEY = "sk-ant-the-key-x7Qa"
HAIKU = SimpleNamespace(
    id="claude-haiku-5-5",
    display_name="Haiku",
    max_tokens=64000,
)
SONNET = SimpleNamespace(
    id="claude-sonnet-5-5",
    display_name="Sonnet",
    max_tokens=32000,
)


# Code
# Stands in for the SDK: the keys it was called with, and its two models
class FakeSdk:
    calls: ClassVar[list[str]] = []
    refused: ClassVar[bool] = False

    def __init__(self) -> None:

        FakeSdk.calls = []
        FakeSdk.refused = False
        self.models = SimpleNamespace(list=self.list)

    def with_options(self, api_key: str) -> FakeSdk:

        FakeSdk.calls.append(api_key)

        return self

    async def list(self) -> AsyncIterator[SimpleNamespace]:

        if FakeSdk.refused:
            request = httpx2.Request("GET", "http://api/v1/models")
            response = httpx2.Response(401, request=request)

            raise AuthenticationError("no", response=response, body=None)

        for model in (HAIKU, SONNET):
            yield model


def put(
    body: Mapping[str, object],
    refused: bool = False,
    http: TestClient = client,
) -> Response:

    fake = FakeSdk()
    FakeSdk.refused = refused

    with patch.object(connections.claude, "sdk", fake):
        return http.put(
            "/chat/settings",
            json={
                "model": "claude-haiku-5-5",
                "max_tokens": 64000,
                "tools_max_turns": 20,
                "show_workspace": False,
                **body,
            },
        )


async def saved_key() -> bytes:

    current_user.set(USER)

    async with db.transaction() as conn:
        result = await conn.execute(text("SELECT api_key FROM settings"))
        key: bytes = result.scalar_one()

        return key


# Who never saved gets the defaults, with the workspace hidden
def test_settings_start_with_the_defaults() -> None:

    response = client.get("/chat/settings")

    assert response.status_code == 200
    assert response.json() == {
        "has_key": False,
        "key_end": None,
        "model": "claude-haiku-5-5",
        "max_tokens": 64000,
        "tools_max_turns": 20,
        "show_workspace": False,
    }


# The front gets only the end of the key, and the table only a token
def test_saved_key_is_encrypted_and_never_comes_back() -> None:

    response = put(body={"api_key": KEY})

    assert response.status_code == 200
    assert KEY not in response.text
    assert response.json()["has_key"] is True
    assert response.json()["key_end"] == "x7Qa"
    token = asyncio.run(saved_key())
    assert KEY.encode() not in token
    assert decrypt(token=token) == KEY
    assert FakeSdk.calls == [KEY]


# A pasted line break is not part of the key
def test_saved_key_loses_the_spaces_around_it() -> None:

    response = put(body={"api_key": f"  {KEY}\n"})

    assert response.json()["key_end"] == "x7Qa"


# Saving without api_key changes the rest and keeps the key
def test_save_without_key_keeps_the_saved_one() -> None:

    put(body={"api_key": KEY})

    response = put(body={"model": "claude-sonnet-5-5", "max_tokens": 1000})

    assert response.json()["has_key"] is True
    assert response.json()["model"] == "claude-sonnet-5-5"
    assert response.json()["max_tokens"] == 1000
    assert decrypt(token=asyncio.run(saved_key())) == KEY


def test_remove_key_keeps_the_other_settings() -> None:

    put(body={"api_key": KEY, "show_workspace": True})

    response = client.delete("/chat/settings/key")

    assert response.status_code == 204
    settings = client.get("/chat/settings").json()
    assert settings["has_key"] is False
    assert settings["key_end"] is None
    assert settings["show_workspace"] is True


def test_refused_key_is_not_saved() -> None:

    response = put(body={"api_key": KEY}, refused=True)

    assert response.status_code == 422
    assert client.get("/chat/settings").json()["has_key"] is False


def test_unknown_model_is_refused() -> None:

    response = put(body={"api_key": KEY, "model": "claude-none"})

    assert response.status_code == 422
    assert "claude-none" in response.json()["detail"]


def test_more_tokens_than_the_model_allows_are_refused() -> None:

    body = {"api_key": KEY, "model": "claude-sonnet-5-5", "max_tokens": 32001}

    response = put(body=body)

    assert response.status_code == 422
    assert "32000" in response.json()["detail"]


def test_max_tokens_must_be_positive() -> None:

    assert put(body={"max_tokens": 0}).status_code == 422


# With nothing to check, the API is not called
def test_showing_the_workspace_needs_no_call_to_the_api() -> None:

    put(body={"api_key": KEY})

    response = put(body={"show_workspace": True}, refused=True)

    assert response.status_code == 200
    assert response.json()["show_workspace"] is True
    assert FakeSdk.calls == []


def test_settings_of_a_user_are_not_seen_by_another() -> None:

    put(body={"api_key": KEY})

    assert other_client.get("/chat/settings").json()["has_key"] is False


def test_each_user_saves_their_own_settings() -> None:

    put(body={"api_key": KEY})

    response = put(body={"show_workspace": True}, http=other_client)

    assert response.status_code == 200
    assert client.get("/chat/settings").json()["show_workspace"] is False


def test_models_of_the_key() -> None:

    put(body={"api_key": KEY})

    with patch.object(connections.claude, "sdk", FakeSdk()):
        response = client.get("/chat/settings/models")

    assert [model["id"] for model in response.json()] == [
        "claude-haiku-5-5", "claude-sonnet-5-5"
    ]
    assert response.json()[1]["max_tokens"] == 32000
    assert FakeSdk.calls == [KEY]


def test_no_models_without_any_key() -> None:

    with patch.object(connections.claude, "sdk", FakeSdk()):
        response = client.get("/chat/settings/models")

    assert response.json() == []


# An answer goes out with the saved key, model and limit
def test_answer_uses_the_saved_settings() -> None:

    body = {"api_key": KEY, "model": "claude-sonnet-5-5", "max_tokens": 1000}
    put(body=body)

    ask(body={"question": "Hi"})

    assert FakeClient.used_key == KEY
    assert FakeMessages.params["model"] == "claude-sonnet-5-5"
    assert FakeMessages.params["max_tokens"] == 1000


# There is no key of the service to fall back on
def test_answer_without_a_key_after_removing_it() -> None:

    put(body={"api_key": KEY})
    client.delete("/chat/settings/key")

    response = ask(body={"question": "Hi"})

    assert response.status_code == 422


def test_workspace_without_a_key_is_refused() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}

    response = create_workspace(ichiro=ichiro, body=body)

    assert response.status_code == 422


# A workspace goes out with the saved model and limit
def test_workspace_uses_the_saved_limit() -> None:

    body = {"api_key": KEY, "model": "claude-sonnet-5-5", "max_tokens": 1000}
    put(body=body)
    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    body = {"folder_id": str(folder), "description": "I play baseball"}

    create_workspace(ichiro=ichiro, body=body)

    assert FakeRunner.params["model"] == "claude-sonnet-5-5"
    assert FakeRunner.params["max_tokens"] == 1000
