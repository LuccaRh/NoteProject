# Imports
from uuid import uuid4

from fastapi.testclient import TestClient
from test_chat import conversation_of, post

from lonzo.main import app


# Global variables
client = TestClient(app)


# Code
def test_conversations_of_a_folder_most_recent_first() -> None:

    folder = str(uuid4())
    older = conversation_of(
        response=post(body={"question": "First", "folder_id": folder}),
    )
    newer = conversation_of(
        response=post(body={"question": "Second", "folder_id": folder}),
    )
    post(body={"question": "Elsewhere", "folder_id": str(uuid4())})

    response = client.get("/chat/conversations", params={"folder_id": folder})

    assert response.status_code == 200
    assert [c["id"] for c in response.json()] == [newer, older]
    assert [c["title"] for c in response.json()] == ["Second", "First"]


def test_conversation_goes_up_when_used_again() -> None:

    folder = str(uuid4())
    older = conversation_of(
        response=post(body={"question": "First", "folder_id": folder}),
    )
    newer = conversation_of(
        response=post(body={"question": "Second", "folder_id": folder}),
    )
    post(body={"question": "Again", "conversation_id": older})

    response = client.get("/chat/conversations", params={"folder_id": folder})

    assert [c["id"] for c in response.json()] == [older, newer]


def test_conversations_of_the_root() -> None:

    root = conversation_of(response=post(body={"question": "At the root"}))
    post(body={"question": "In a folder", "folder_id": str(uuid4())})

    response = client.get("/chat/conversations")

    assert root in [c["id"] for c in response.json()]
    assert all(c["folder_id"] is None for c in response.json())


def test_conversation_with_its_messages() -> None:

    conversation_id = conversation_of(response=post(body={"question": "Hi"}))

    response = client.get(f"/chat/conversations/{conversation_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Hi"
    assert [m["role"] for m in body["messages"]] == ["user", "assistant"]
    assert body["messages"][1]["content"] == [
        {"type": "text", "text": "Hello there"}
    ]


def test_missing_conversation() -> None:

    response = client.get(f"/chat/conversations/{uuid4()}")

    assert response.status_code == 404
