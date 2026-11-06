# Imports
import asyncio
from collections.abc import Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fakes import FakeIchiro

from lonzo.core import connections
from lonzo.services.note_tools import NoteTools


# Global variables
TOOLS = {tool.name: tool for tool in NoteTools().tools()}


# Code
# Two workspaces, each with a note about bats, one of them deeper
@pytest.fixture
def ichiro() -> Iterator[FakeIchiro]:

    fake = FakeIchiro()
    baseball = fake.add(title="Baseball", is_folder=True)
    stats = fake.add(title="Stats", parent_id=baseball, is_folder=True)
    fake.add(title="Batting", parent_id=stats, body="Bats left, hits far.")
    calculus = fake.add(title="Calculus", is_folder=True)
    fake.add(title="Limits", parent_id=calculus, body="No bats here.")

    with patch.object(connections.ichiro, "http", fake.client()):
        yield fake


def call(name: str, **params: object) -> str:

    # Tool input comes as JSON, so ids go as strings
    tool_input = {
        key: str(value) if isinstance(value, UUID) else value
        for key, value in params.items()
    }

    return str(asyncio.run(TOOLS[name].call(tool_input)))


def id_of(fake: FakeIchiro, title: str) -> UUID:

    return next(
        UUID(str(row["id"]))
        for row in fake.rows.values()
        if row["title"] == title
    )


def test_search_notes_everywhere(ichiro: FakeIchiro) -> None:

    found = call(name="search_notes", query="bats")

    assert "Batting" in found
    assert "Limits" in found


def test_search_notes_inside_a_folder(ichiro: FakeIchiro) -> None:

    baseball = id_of(fake=ichiro, title="Baseball")
    found = call(name="search_notes", query="bats", folder_id=baseball)

    assert found == f"{id_of(fake=ichiro, title='Batting')} Batting"


def test_search_notes_with_no_match(ichiro: FakeIchiro) -> None:

    assert call(name="search_notes", query="pitching") == "no notes found"


def test_search_titles_finds_folders_by_part_of_the_name(
    ichiro: FakeIchiro,
) -> None:

    found = call(name="search_titles", text="base")

    assert found == f"{id_of(fake=ichiro, title='Baseball')} Baseball/"


def test_list_folder_at_the_top(ichiro: FakeIchiro) -> None:

    listing = call(name="list_folder").splitlines()

    assert [line.split(" ", 1)[1] for line in listing] == [
        "Baseball/",
        "Calculus/",
    ]


def test_list_folder_inside_a_folder(ichiro: FakeIchiro) -> None:

    stats = id_of(fake=ichiro, title="Stats")

    assert call(name="list_folder", folder_id=stats).endswith(" Batting")


def test_read_note(ichiro: FakeIchiro) -> None:

    batting = id_of(fake=ichiro, title="Batting")

    assert call(name="read_note", note_id=batting) == (
        "# Batting\n\nBats left, hits far."
    )


def test_read_note_of_a_folder(ichiro: FakeIchiro) -> None:

    stats = id_of(fake=ichiro, title="Stats")

    with pytest.raises(ValueError, match="is a folder"):
        call(name="read_note", note_id=stats)


def test_create_note_at_the_root(ichiro: FakeIchiro) -> None:

    answer = call(name="create_note", path="/Ideas", body="Fly.")

    note_id = id_of(fake=ichiro, title="Ideas")
    row = ichiro.rows[note_id]
    assert answer == f"created {note_id} /Ideas"
    assert row["parent_id"] is None
    assert row["body"] == "Fly."


def test_create_note_in_any_workspace(ichiro: FakeIchiro) -> None:

    calculus = id_of(fake=ichiro, title="Calculus")
    call(name="create_note", path="/Calculus/Series/Taylor", body="Sums.")

    series = id_of(fake=ichiro, title="Series")
    assert ichiro.rows[series]["parent_id"] == str(calculus)
    taylor = ichiro.rows[id_of(fake=ichiro, title="Taylor")]
    assert taylor["parent_id"] == str(series)


def test_create_folder_at_the_root(ichiro: FakeIchiro) -> None:

    assert call(name="create_folder", path="/Physics") == "created /Physics/"
    assert ichiro.rows[id_of(fake=ichiro, title="Physics")]["is_folder"]


def test_create_note_refuses_a_path_from_nowhere(ichiro: FakeIchiro) -> None:

    with pytest.raises(ValueError, match="must be a whole path"):
        call(name="create_note", path="kb/Summary", body="Sums.")

    assert "kb" not in {row["title"] for row in ichiro.rows.values()}


def test_create_note_refuses_an_unknown_first_folder(
    ichiro: FakeIchiro,
) -> None:

    with pytest.raises(ValueError, match="no folder /kb at the root"):
        call(name="create_note", path="/kb/Summary", body="Sums.")

    assert "kb" not in {row["title"] for row in ichiro.rows.values()}


def test_edit_note_changes_only_the_piece(ichiro: FakeIchiro) -> None:

    batting = id_of(fake=ichiro, title="Batting")
    edited = call(
        name="edit_note",
        note_id=batting,
        old_text="left",
        new_text="right",
    )

    assert edited == "edited Batting"
    assert ichiro.rows[batting]["body"] == "Bats right, hits far."


def test_edit_note_without_the_old_text(ichiro: FakeIchiro) -> None:

    batting = id_of(fake=ichiro, title="Batting")

    with pytest.raises(ValueError, match="is not in Batting"):
        call(name="edit_note", note_id=batting, old_text="x", new_text="y")


def test_edit_note_with_the_old_text_twice(ichiro: FakeIchiro) -> None:

    batting = id_of(fake=ichiro, title="Batting")

    with pytest.raises(ValueError, match="is 2 times in Batting"):
        call(name="edit_note", note_id=batting, old_text="ts", new_text="")

    assert ichiro.rows[batting]["body"] == "Bats left, hits far."


def test_delete_a_folder_with_what_is_inside(ichiro: FakeIchiro) -> None:

    stats = id_of(fake=ichiro, title="Stats")

    assert call(name="delete_note", note_id=stats) == f"deleted {stats}"
    titles = {row["title"] for row in ichiro.rows.values()}
    assert titles == {"Baseball", "Calculus", "Limits"}


def test_delete_a_missing_note(ichiro: FakeIchiro) -> None:

    with pytest.raises(ValueError, match="there is no note"):
        call(name="delete_note", note_id=uuid4())


def test_target_is_the_search_or_the_last_name_of_the_path() -> None:

    tools = NoteTools()

    assert tools.target(tool_input={"query": "bats"}) == "bats"
    assert tools.target(tool_input={"text": "bat"}) == "bat"
    assert tools.target(tool_input={"path": "Games/Chess/"}) == "Chess"


def test_target_is_none_before_the_input_comes() -> None:

    assert NoteTools().target(tool_input={}) is None


def test_target_is_the_title_of_a_note_seen_by_a_search(
    ichiro: FakeIchiro,
) -> None:

    tools = NoteTools()
    by_name = {tool.name: tool for tool in tools.tools()}
    asyncio.run(by_name["search_notes"].call({"query": "left"}))
    note_id = str(id_of(fake=ichiro, title="Batting"))

    assert tools.target(tool_input={"note_id": note_id}) == "Batting"
    assert tools.target(tool_input={"note_id": str(uuid4())}) is None


def test_target_is_the_title_of_a_folder_seen_in_a_listing(
    ichiro: FakeIchiro,
) -> None:

    tools = NoteTools()
    by_name = {tool.name: tool for tool in tools.tools()}
    asyncio.run(by_name["list_folder"].call({}))
    folder_id = str(id_of(fake=ichiro, title="Baseball"))

    assert tools.target(tool_input={"folder_id": folder_id}) == "Baseball"


def test_target_is_the_title_of_a_note_just_created(
    ichiro: FakeIchiro,
) -> None:

    tools = NoteTools()
    by_name = {tool.name: tool for tool in tools.tools()}
    body = {"path": "/Baseball/Chess", "body": "Openings"}
    asyncio.run(by_name["create_note"].call(body))
    note_id = str(id_of(fake=ichiro, title="Chess"))

    assert tools.target(tool_input={"note_id": note_id}) == "Chess"
