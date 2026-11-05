# Imports
from fastapi.testclient import TestClient
from test_notes import create

from ichiro.main import app


# Code
# A note of one user is not in the list, the tree or the search of another
def test_other_user_does_not_see_the_note(
    client: TestClient,
    other_client: TestClient,
) -> None:

    create(client=client, title="Diary", body="zorblax")

    assert other_client.get("/notes").json() == []
    assert other_client.get("/notes/tree").json() == []

    response = other_client.get("/notes/search", params={"q": "zorblax"})
    assert response.json() == []

    response = other_client.get("/notes/search-titles", params={"q": "Dia"})
    assert response.json() == []


# Reading, editing and deleting a note of another user is a 404
def test_other_user_can_not_touch_the_note(
    client: TestClient,
    other_client: TestClient,
) -> None:

    note = create(client=client, title="Diary")
    url = f"/notes/{note['id']}"

    assert other_client.get(url).status_code == 404
    assert other_client.patch(url, json={"body": "x"}).status_code == 404
    assert other_client.delete(url).status_code == 404

    # Still there, untouched, for its owner
    assert client.get(url).json()["body"] == ""


# A folder of another user can't hold a new note
def test_other_user_can_not_write_in_the_folder(
    client: TestClient,
    other_client: TestClient,
) -> None:

    folder = create(client=client, title="Work", is_folder=True)

    response = other_client.post(
        "/notes",
        json={"title": "Spy", "parent_id": folder["id"]},
    )
    assert response.status_code == 422


# Each user has their own root: the same title doesn't collide
def test_same_title_for_two_users(
    client: TestClient,
    other_client: TestClient,
) -> None:

    create(client=client, title="Inbox")
    create(client=other_client, title="Inbox")


# Without the X-User-Id from Caddy, or with a broken one: 401
def test_no_user_is_refused() -> None:

    assert TestClient(app).get("/notes").status_code == 401

    response = TestClient(app, headers={"X-User-Id": "1"}).get("/notes")
    assert response.status_code == 401
