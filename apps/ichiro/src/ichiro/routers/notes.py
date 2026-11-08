# Imports
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from ichiro.schemas.notes import (
    Note,
    NoteCreate,
    NoteMatch,
    NotePath,
    NoteUpdate,
    TitleMatch,
)
from ichiro.services.notes import (
    create_note,
    find_above,
    find_by_path,
    find_note,
    find_path,
    list_notes,
    list_tree,
    remove_note,
    search_notes,
    search_titles,
    update_note,
)


# Global variables
router = APIRouter(prefix="/notes")


# Code
@router.get("")
def get_notes(
    parent_id: UUID | None = None,
    title: str | None = None,
) -> list[Note]:
    """
    Notes right inside parent_id (the root when none), folders first,
    then by title; only the ones with this title when one is given
    """

    return list_notes(parent_id=parent_id, title=title)


@router.get("/tree")
def get_tree(parent_id: UUID | None = None) -> list[NotePath]:
    """
    Everything inside parent_id, at any depth, each with its path of
    titles from there; 404 when parent_id doesn't exist
    """

    return list_tree(parent_id=parent_id)


@router.get("/by-path")
def get_by_path(path: str, parent_id: UUID | None = None) -> Note:
    """
    The note at a path of titles (a/b/c) from parent_id (the root when
    none); 404 when a name on the way is missing
    """

    return find_by_path(path=path, parent_id=parent_id)


@router.get("/search")
def get_search(
    q: Annotated[str, Query(min_length=1)],
    parent_id: UUID | None = None,
) -> list[NoteMatch]:
    """
    Notes (not folders) whose title or body has the words of q, by
    title; only the ones inside parent_id, at any depth, when one is
    given; 404 when parent_id doesn't exist
    """

    return search_notes(query=q, parent_id=parent_id)


@router.get("/search-titles")
def get_search_titles(
    q: Annotated[str, Query(min_length=1)],
    parent_id: UUID | None = None,
) -> list[TitleMatch]:
    """
    Notes and folders whose title contains q, even mid-word, by title;
    only the ones inside parent_id, at any depth, when one is given;
    404 when parent_id doesn't exist
    """

    return search_titles(text_in_title=q, parent_id=parent_id)


@router.get("/{note_id}")
def get_note(note_id: UUID) -> Note:
    """
    One note by id; 404 when it doesn't exist
    """

    return find_note(note_id=note_id)


@router.get("/{note_id}/path")
def get_path(note_id: UUID) -> NotePath:
    """
    A note with its path of titles from the root; 404 when it doesn't
    exist
    """

    return find_path(note_id=note_id)


@router.get("/{note_id}/above")
def get_above(note_id: UUID, path: str) -> list[Note]:
    """
    The note at a path of titles (a/b) inside each folder above note_id,
    the root too, from the root down; 404 when note_id doesn't exist
    """

    return find_above(note_id=note_id, path=path)


@router.post("", status_code=201)
def post_note(note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

    return create_note(note=note)


@router.patch("/{note_id}")
def patch_note(note_id: UUID, patch: NoteUpdate) -> Note:
    """
    Changes only the fields sent: title, body or parent (a move)
    """

    return update_note(note_id=note_id, patch=patch)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: UUID) -> Response:
    """
    Deletes a note, or a folder with everything inside it
    """

    remove_note(note_id=note_id)

    return Response(status_code=204)
