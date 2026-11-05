# Imports
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


# Global variables
MISSING_ID = "00000000-0000-0000-0000-000000000000"


# Code
# POST a note and return its JSON, failing the test if it isn't 201
def create(
    client: TestClient,
    title: str,
    **fields: Any,
) -> dict[str, Any]:

    response = client.post("/notes", json={"title": title, **fields})
    assert response.status_code == 201

    note: dict[str, Any] = response.json()

    return note


# A created note comes back the same from GET, at the root
def test_create_returns_the_note(client: TestClient) -> None:

    note = create(client=client, title="Groceries", body="milk")
    response = client.get(f"/notes/{note['id']}")

    assert response.status_code == 200
    assert response.json() == note
    assert note["parent_id"] is None
    assert note["is_folder"] is False


# GET of an unknown id is 404
def test_get_missing_note(client: TestClient) -> None:

    response = client.get(f"/notes/{MISSING_ID}")

    assert response.status_code == 404


# Inside a folder: folders first, then the rest by title
def test_list_folders_first_then_by_title(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="b note", parent_id=folder["id"])
    create(client=client, title="a note", parent_id=folder["id"])
    create(
        client=client,
        title="c folder",
        parent_id=folder["id"],
        is_folder=True,
    )

    response = client.get("/notes", params={"parent_id": folder["id"]})
    titles = [note["title"] for note in response.json()]

    assert titles == ["c folder", "a note", "b note"]


# Without parent_id the list has only the root
def test_list_root(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="Inside", parent_id=folder["id"])

    titles = [note["title"] for note in client.get("/notes").json()]

    assert "Work" in titles
    assert "Inside" not in titles


# POST into an unknown parent is 422
def test_create_in_missing_parent(client: TestClient) -> None:

    response = client.post(
        "/notes",
        json={"title": "Orphan", "parent_id": MISSING_ID},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "parent not found"


# POST into a note that isn't a folder is 422
def test_create_inside_a_note(client: TestClient) -> None:

    note = create(client=client, title="Plain note")
    response = client.post(
        "/notes",
        json={"title": "Child", "parent_id": note["id"]},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "parent is not a folder"


# PATCH changes only the fields sent and bumps updated_at
def test_update_only_the_fields_sent(client: TestClient) -> None:

    note = create(client=client, title="Old", body="kept")
    response = client.patch(f"/notes/{note['id']}", json={"title": "New"})
    updated = response.json()

    assert response.status_code == 200
    assert updated["title"] == "New"
    assert updated["body"] == "kept"
    assert updated["updated_at"] >= note["updated_at"]


# PATCH can't set title to null
def test_update_title_to_null(client: TestClient) -> None:

    note = create(client=client, title="Title")
    response = client.patch(f"/notes/{note['id']}", json={"title": None})

    assert response.status_code == 422


# PATCH of an unknown id is 404
def test_update_missing_note(client: TestClient) -> None:

    response = client.patch(f"/notes/{MISSING_ID}", json={"title": "New"})

    assert response.status_code == 404


# parent_id moves the note; null moves it back to the root
def test_move_to_folder_and_back_to_root(client: TestClient) -> None:

    folder = create(client=client, title="Folder", is_folder=True)
    note = create(client=client, title="Note")
    url = f"/notes/{note['id']}"

    moved = client.patch(url, json={"parent_id": folder["id"]}).json()
    assert moved["parent_id"] == folder["id"]

    back = client.patch(url, json={"parent_id": None}).json()
    assert back["parent_id"] is None


# A folder can't be its own parent
def test_move_folder_inside_itself(client: TestClient) -> None:

    folder = create(client=client, title="Folder", is_folder=True)
    response = client.patch(
        f"/notes/{folder['id']}",
        json={"parent_id": folder["id"]},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "cannot move a folder inside itself"


# A folder can't go below itself, and stays where it was
def test_move_folder_inside_its_subfolder(client: TestClient) -> None:

    top = create(client=client, title="Top", is_folder=True)
    middle = create(
        client=client,
        title="Middle",
        parent_id=top["id"],
        is_folder=True,
    )
    bottom = create(
        client=client,
        title="Bottom",
        parent_id=middle["id"],
        is_folder=True,
    )

    response = client.patch(
        f"/notes/{top['id']}",
        json={"parent_id": bottom["id"]},
    )

    assert response.status_code == 422
    assert client.get(f"/notes/{top['id']}").json()["parent_id"] is None


# Deleting a folder deletes what is inside it
def test_delete_folder_deletes_its_notes(client: TestClient) -> None:

    folder = create(client=client, title="Folder", is_folder=True)
    note = create(client=client, title="Inside", parent_id=folder["id"])

    assert client.delete(f"/notes/{folder['id']}").status_code == 204
    assert client.get(f"/notes/{note['id']}").status_code == 404


# DELETE of an unknown id is 404
def test_delete_missing_note(client: TestClient) -> None:

    response = client.delete(f"/notes/{MISSING_ID}")

    assert response.status_code == 404


# With title, the list has only the note with that title in the folder
def test_list_by_title(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    note = create(client=client, title="Plan", parent_id=folder["id"])
    create(client=client, title="Other", parent_id=folder["id"])
    create(client=client, title="Plan")

    params = {"parent_id": folder["id"], "title": "Plan"}
    response = client.get("/notes", params=params)

    assert response.json() == [note]


# A title that isn't in the folder gives an empty list
def test_list_by_missing_title(client: TestClient) -> None:

    create(client=client, title="Plan")

    response = client.get("/notes", params={"title": "Nothing here"})

    assert response.json() == []


# Two notes with the same title in one folder: the second POST is 409
def test_create_title_taken(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="Plan", parent_id=folder["id"])

    body = {"title": "Plan", "parent_id": folder["id"]}
    response = client.post("/notes", json=body)

    assert response.status_code == 409


# The root is a folder too: the same title twice there is 409
def test_create_title_taken_at_root(client: TestClient) -> None:

    create(client=client, title="Plan")

    response = client.post("/notes", json={"title": "Plan"})

    assert response.status_code == 409


# The same title in another folder is fine
def test_same_title_in_other_folder(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="Plan")

    create(client=client, title="Plan", parent_id=folder["id"])


# Renaming to a title taken in the folder is 409
def test_rename_to_title_taken(client: TestClient) -> None:

    create(client=client, title="Plan")
    note = create(client=client, title="Draft")

    response = client.patch(f"/notes/{note['id']}", json={"title": "Plan"})

    assert response.status_code == 409


# Moving into a folder that has a note with the same title is 409
def test_move_to_title_taken(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="Plan", parent_id=folder["id"])
    note = create(client=client, title="Plan")

    body = {"parent_id": folder["id"]}
    response = client.patch(f"/notes/{note['id']}", json=body)

    assert response.status_code == 409


# A path of titles from a folder finds the note at its end
def test_get_by_path(client: TestClient) -> None:

    top = create(client=client, title="Work", is_folder=True)
    middle = create(
        client=client,
        title="Plans",
        parent_id=top["id"],
        is_folder=True,
    )
    note = create(client=client, title="Week", parent_id=middle["id"])

    params = {"parent_id": top["id"], "path": "Plans/Week"}
    response = client.get("/notes/by-path", params=params)

    assert response.status_code == 200
    assert response.json() == note


# Without parent_id the path starts at the root; extra slashes are fine
def test_get_by_path_from_root(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    note = create(client=client, title="Plan", parent_id=folder["id"])

    params = {"path": "/Work//Plan/"}
    response = client.get("/notes/by-path", params=params)

    assert response.json() == note


# A path that ends at a folder gives the folder
def test_get_folder_by_path(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)

    response = client.get("/notes/by-path", params={"path": "Work"})

    assert response.json() == folder


# A missing name anywhere on the way is 404
def test_get_by_missing_path(client: TestClient) -> None:

    create(client=client, title="Work", is_folder=True)

    params = {"path": "Work/Nothing here"}
    response = client.get("/notes/by-path", params=params)

    assert response.status_code == 404


# A path with no names is 422
def test_get_by_empty_path(client: TestClient) -> None:

    response = client.get("/notes/by-path", params={"path": "//"})

    assert response.status_code == 422


# The path of a note goes from the root, through every folder above it
def test_path_of_a_note(client: TestClient) -> None:

    top = create(client=client, title="Work", is_folder=True)
    plans = create(
        client=client,
        title="Plans",
        parent_id=top["id"],
        is_folder=True,
    )
    week = create(client=client, title="Week", parent_id=plans["id"])

    response = client.get(f"/notes/{week['id']}/path")

    assert response.status_code == 200
    assert response.json() == {
        "id": week["id"],
        "path": "Work/Plans/Week",
        "is_folder": False,
    }


# A note at the root is its own path
def test_path_of_a_note_at_the_root(client: TestClient) -> None:

    work = create(client=client, title="Work", is_folder=True)

    response = client.get(f"/notes/{work['id']}/path")

    assert response.json()["path"] == "Work"


def test_path_of_a_missing_note(client: TestClient) -> None:

    response = client.get(f"/notes/{uuid4()}/path")

    assert response.status_code == 404


# The tree of a folder: every level, with paths, in file tree order
def test_tree_of_a_folder(client: TestClient) -> None:

    top = create(client=client, title="Work", is_folder=True)
    plans = create(
        client=client,
        title="Plans",
        parent_id=top["id"],
        is_folder=True,
    )
    week = create(client=client, title="Week", parent_id=plans["id"])
    zebra = create(client=client, title="Zebra", parent_id=top["id"])

    params = {"parent_id": top["id"]}
    response = client.get("/notes/tree", params=params)

    assert response.status_code == 200
    assert response.json() == [
        {"id": plans["id"], "path": "Plans", "is_folder": True},
        {"id": week["id"], "path": "Plans/Week", "is_folder": False},
        {"id": zebra["id"], "path": "Zebra", "is_folder": False},
    ]


# Without parent_id the tree starts at the root
def test_tree_of_the_root(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)
    create(client=client, title="Plan", parent_id=folder["id"])

    paths = [item["path"] for item in client.get("/notes/tree").json()]

    assert "Work" in paths
    assert "Work/Plan" in paths


# An empty folder has an empty tree
def test_tree_of_an_empty_folder(client: TestClient) -> None:

    folder = create(client=client, title="Work", is_folder=True)

    params = {"parent_id": folder["id"]}
    response = client.get("/notes/tree", params=params)

    assert response.json() == []


# The tree of an unknown folder is 404
def test_tree_of_a_missing_folder(client: TestClient) -> None:

    params = {"parent_id": MISSING_ID}
    response = client.get("/notes/tree", params=params)

    assert response.status_code == 404


# Search finds the word in the title or the body, notes only, by title
def test_search_title_and_body(client: TestClient) -> None:

    in_body = create(client=client, title="Beta", body="the Zorblax, again")
    in_title = create(client=client, title="Alpha zorblax")
    create(client=client, title="Zorblax", is_folder=True)
    create(client=client, title="Other", body="zorbl zorblaxes")

    response = client.get("/notes/search", params={"q": "zorblax"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": in_title["id"], "title": "Alpha zorblax"},
        {"id": in_body["id"], "title": "Beta"},
    ]


# Two words: only the notes that have both
def test_search_two_words(client: TestClient) -> None:

    both = create(client=client, title="Both", body="quixel and vormic")
    create(client=client, title="One", body="quixel only")

    response = client.get("/notes/search", params={"q": "vormic quixel"})

    assert response.json() == [{"id": both["id"], "title": "Both"}]


# With parent_id, only the notes inside that folder, at any depth
def test_search_inside_a_folder(client: TestClient) -> None:

    folder = create(client=client, title="Search", is_folder=True)
    sub = create(
        client=client,
        title="Sub",
        is_folder=True,
        parent_id=folder["id"],
    )
    deep = create(
        client=client,
        title="Deep",
        body="plonkite",
        parent_id=sub["id"],
    )
    create(client=client, title="Outside", body="plonkite")

    response = client.get(
        "/notes/search",
        params={"q": "plonkite", "parent_id": folder["id"]},
    )

    assert response.json() == [{"id": deep["id"], "title": "Deep"}]


# A parent_id that doesn't exist is 404
def test_search_inside_a_missing_folder(client: TestClient) -> None:

    response = client.get(
        "/notes/search",
        params={"q": "plonkite", "parent_id": MISSING_ID},
    )

    assert response.status_code == 404


# An empty query is 422
def test_search_empty_query(client: TestClient) -> None:

    response = client.get("/notes/search", params={"q": ""})

    assert response.status_code == 422


# Title search finds the text mid-word, in notes and folders, by title
def test_search_titles_mid_word(client: TestClient) -> None:

    folder = create(client=client, title="Old Wumbleton", is_folder=True)
    note = create(client=client, title="A WUMBLETON list")
    create(client=client, title="Other", body="wumbleton")

    response = client.get("/notes/search-titles", params={"q": "umblet"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": note["id"], "title": "A WUMBLETON list", "is_folder": False},
        {"id": folder["id"], "title": "Old Wumbleton", "is_folder": True},
    ]


# % and _ in the text match themselves, not any text
def test_search_titles_wildcards(client: TestClient) -> None:

    match = create(client=client, title="Grobnik 100% done")
    create(client=client, title="Grobnik 100 done")

    response = client.get("/notes/search-titles", params={"q": "grobnik 100%"})

    assert response.json() == [
        {"id": match["id"], "title": "Grobnik 100% done", "is_folder": False},
    ]


# With parent_id, only the titles inside that folder, at any depth
def test_search_titles_inside_a_folder(client: TestClient) -> None:

    folder = create(client=client, title="Titles", is_folder=True)
    sub = create(
        client=client,
        title="Fizzlecrank sub",
        is_folder=True,
        parent_id=folder["id"],
    )
    create(client=client, title="Fizzlecrank outside")

    response = client.get(
        "/notes/search-titles",
        params={"q": "fizzlecrank", "parent_id": folder["id"]},
    )

    assert response.json() == [
        {"id": sub["id"], "title": "Fizzlecrank sub", "is_folder": True},
    ]


# A parent_id that doesn't exist is 404, an empty text is 422
def test_search_titles_bad_params(client: TestClient) -> None:

    missing = client.get(
        "/notes/search-titles",
        params={"q": "x", "parent_id": MISSING_ID},
    )
    empty = client.get("/notes/search-titles", params={"q": ""})

    assert missing.status_code == 404
    assert empty.status_code == 422
