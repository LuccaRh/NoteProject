# Imports
import pytest
from fakes import OTHER_USER
from fastapi.testclient import TestClient
from test_chat import conversation_of, post

from lonzo.main import app


# Global variables
pytestmark = pytest.mark.usefixtures("saved_key")
other_client = TestClient(app, headers={"X-User-Id": str(OTHER_USER)})


# Code
# A conversation of one user is not in the list of another
def test_other_user_does_not_list_the_conversation() -> None:

    conversation_id = conversation_of(response=post(body={"question": "Hi"}))

    response = other_client.get("/chat/conversations")

    assert response.status_code == 200
    assert conversation_id not in [c["id"] for c in response.json()]


# Opening a conversation of another user is a 404, messages included
def test_other_user_can_not_open_the_conversation() -> None:

    conversation_id = conversation_of(response=post(body={"question": "Hi"}))

    response = other_client.get(f"/chat/conversations/{conversation_id}")

    assert response.status_code == 404


# Without the X-User-Id from Caddy: 401
def test_no_user_is_refused() -> None:

    assert TestClient(app).get("/chat/conversations").status_code == 401
