# Imports
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fakes import OTHER_USER, USER, FakeIchiro
from fastapi.testclient import TestClient
from httpx2 import Response

from lonzo.core import connections
from lonzo.main import app
from lonzo.services.workspaces import is_skill_path, split_skill


# Global variables
client = TestClient(app, headers={"X-User-Id": str(USER)})
other_client = TestClient(app, headers={"X-User-Id": str(OTHER_USER)})


# Code
def workspace(ichiro: FakeIchiro, title: str) -> tuple[UUID, UUID]:

    folder = ichiro.add(title=title, is_folder=True)
    dot = ichiro.add(title=".workspace", parent_id=folder, is_folder=True)
    skills = ichiro.add(title="skills", parent_id=dot, is_folder=True)

    return folder, skills


def request(
    ichiro: FakeIchiro,
    method: str,
    url: str,
    body: dict[str, str] | None = None,
    user: TestClient = client,
) -> Response:

    with patch.object(connections.ichiro, "http", ichiro.client()):
        return user.request(method, url, json=body)


def publish(ichiro: FakeIchiro, note: UUID) -> Response:

    body = {"note_id": str(note)}

    return request(ichiro=ichiro, method="POST", url="/chat/skills", body=body)


def test_split_skill_skips_blank_lines_and_heading_marks() -> None:

    assert split_skill(body="\n# Does X.\n\nSteps") == ("Does X.", "Steps")


@pytest.mark.parametrize(
    "description",
    ["Does X. Use when Y", '"Does X. Use when Y"', "'Does X. Use when Y'"],
)
def test_split_skill_takes_the_description_of_the_header(
    description: str,
) -> None:

    body = f"---\nname: swing\ndescription: {description}\n---\n\nSteps"

    assert split_skill(body=body) == ("Does X. Use when Y", "Steps")


def test_split_skill_keeps_the_indentation_of_the_steps() -> None:

    body = "---\ndescription: Does X.\n---\n\n- One\n    - Two"

    assert split_skill(body=body) == ("Does X.", "- One\n    - Two")


def test_split_skill_without_a_description_keeps_the_first_line() -> None:

    assert split_skill(body="---\nname: swing") == ("---", "name: swing")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("Baseball/.workspace/skills/swing", True),
        (".workspace/skills/swing", True),
        ("Baseball/skills/swing", False),
        ("Baseball/.workspace/skills", False),
    ],
)
def test_is_skill_path(path: str, expected: bool) -> None:

    assert is_skill_path(path=path) is expected


def test_workspace_lists_its_skills() -> None:

    ichiro = FakeIchiro()
    folder, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="# Does X.\nSteps")
    url = f"/chat/workspaces/{folder}/skills"

    response = request(ichiro=ichiro, method="GET", url=url)

    assert response.json() == [
        {"id": str(note), "title": "swing", "summary": "Does X."},
    ]


def test_folder_without_a_workspace_lists_nothing() -> None:

    ichiro = FakeIchiro()
    folder = ichiro.add(title="Baseball", is_folder=True)
    url = f"/chat/workspaces/{folder}/skills"

    assert request(ichiro=ichiro, method="GET", url=url).json() == []


def test_publish_splits_the_note_and_anyone_lists_it() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.\n\nSteps")

    response = publish(ichiro=ichiro, note=note)
    listed = request(
        ichiro=ichiro,
        method="GET",
        url="/chat/skills",
        user=other_client,
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "Does X."
    assert response.json()["body"] == "Steps"
    assert response.json() in listed.json()


def test_publishing_again_updates_the_same_row() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    first = publish(ichiro=ichiro, note=note).json()

    ichiro.rows[note]["body"] = "Does Y."
    second = publish(ichiro=ichiro, note=note).json()

    assert second["id"] == first["id"]
    assert second["summary"] == "Does Y."


def test_owner_me_keeps_only_the_skills_of_the_person() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    skill = publish(ichiro=ichiro, note=note).json()

    mine = request(ichiro=ichiro, method="GET", url="/chat/skills?owner=me")
    theirs = request(
        ichiro=ichiro,
        method="GET",
        url="/chat/skills?owner=me",
        user=other_client,
    )

    assert mine.json() == [skill]
    assert theirs.json() == []


def test_the_default_list_leaves_out_the_skills_of_the_person() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    skill = publish(ichiro=ichiro, note=note).json()

    listed = request(ichiro=ichiro, method="GET", url="/chat/skills")

    assert skill not in listed.json()


def test_only_a_note_in_a_skills_folder_is_published() -> None:

    ichiro = FakeIchiro()
    note = ichiro.add(title="swing", body="Does X.")

    response = publish(ichiro=ichiro, note=note)

    assert response.status_code == 422


def test_an_empty_skill_is_not_published() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills)

    assert publish(ichiro=ichiro, note=note).status_code == 422


def test_published_skill_is_copied_for_someone_else() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.\n\nSteps")
    skill = publish(ichiro=ichiro, note=note).json()
    target, target_skills = workspace(ichiro=ichiro, title="Golf")

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{target}/skills",
        body={"skill_id": skill["id"]},
        user=other_client,
    )

    assert response.status_code == 201
    assert response.json()["title"] == "swing"
    assert response.json()["parent_id"] == str(target_skills)
    assert response.json()["body"] == (
        "---\nname: swing\ndescription: Does X.\n---\n\nSteps"
    )


def test_own_note_is_copied_to_another_workspace() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    target, target_skills = workspace(ichiro=ichiro, title="Golf")

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{target}/skills",
        body={"note_id": str(note)},
    )

    assert response.status_code == 201
    assert response.json()["parent_id"] == str(target_skills)
    assert ichiro.rows[note]["body"] == "Does X."


def test_adding_recreates_a_deleted_skills_folder() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    target, target_skills = workspace(ichiro=ichiro, title="Golf")
    del ichiro.rows[target_skills]

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{target}/skills",
        body={"note_id": str(note)},
    )

    assert response.status_code == 201
    assert response.json()["parent_id"] != str(target_skills)


def test_adding_twice_is_a_conflict() -> None:

    ichiro = FakeIchiro()
    folder, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{folder}/skills",
        body={"note_id": str(note)},
    )

    assert response.status_code == 409


def test_adding_needs_a_workspace() -> None:

    ichiro = FakeIchiro()
    _, skills = workspace(ichiro=ichiro, title="Baseball")
    note = ichiro.add(title="swing", parent_id=skills, body="Does X.")
    folder = ichiro.add(title="Golf", is_folder=True)

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{folder}/skills",
        body={"note_id": str(note)},
    )

    assert response.status_code == 422


def test_adding_a_missing_skill_is_a_404() -> None:

    ichiro = FakeIchiro()
    folder, _ = workspace(ichiro=ichiro, title="Baseball")

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{folder}/skills",
        body={"skill_id": str(uuid4())},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "body",
    [{}, {"skill_id": str(uuid4()), "note_id": str(uuid4())}],
)
def test_adding_needs_exactly_one_source(body: dict[str, str]) -> None:

    ichiro = FakeIchiro()
    folder, _ = workspace(ichiro=ichiro, title="Baseball")

    response = request(
        ichiro=ichiro,
        method="POST",
        url=f"/chat/workspaces/{folder}/skills",
        body=body,
    )

    assert response.status_code == 422
