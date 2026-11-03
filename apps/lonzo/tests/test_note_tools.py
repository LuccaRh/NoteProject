# Imports
import asyncio
from collections.abc import Iterator
from unittest.mock import patch
from uuid import UUID

import pytest
from fakes import FakeIchiro

from lonzo import connections
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
