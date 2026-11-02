# Imports
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import Connection

from ichiro.db import get_conn
from ichiro.schemas.notes import Note, NoteCreate, NotePath, NoteUpdate
from ichiro.services.notes import (
    create_note,
    find_by_path,
    find_note,
    list_notes,
    list_tree,
    remove_note,
    update_note,
)


# Global variables
router = APIRouter(prefix="/notes")
Conn = Annotated[Connection, Depends(get_conn)]


# Code
@router.get("")
def get_notes(
    conn: Conn,
    parent_id: UUID | None = None,
    title: str | None = None,
) -> list[Note]:
    """
    Notes right inside parent_id (the root when none), folders first,
    then by title; only the ones with this title when one is given
    """

    return list_notes(conn=conn, parent_id=parent_id, title=title)


@router.get("/tree")
def get_tree(conn: Conn, parent_id: UUID | None = None) -> list[NotePath]:
    """
    Everything inside parent_id, at any depth, each with its path of
    titles from there; 404 when parent_id doesn't exist
    """

    return list_tree(conn=conn, parent_id=parent_id)


@router.get("/by-path")
def get_by_path(
    conn: Conn,
    path: str,
    parent_id: UUID | None = None,
) -> Note:
    """
    The note at a path of titles (a/b/c) from parent_id (the root when
    none); 404 when a name on the way is missing
    """

    return find_by_path(conn=conn, path=path, parent_id=parent_id)


@router.get("/{note_id}")
def get_note(conn: Conn, note_id: UUID) -> Note:
    """
    One note by id; 404 when it doesn't exist
    """

    return find_note(conn=conn, note_id=note_id)


@router.post("", status_code=201)
def post_note(conn: Conn, note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

    return create_note(conn=conn, note=note)


@router.patch("/{note_id}")
def patch_note(conn: Conn, note_id: UUID, patch: NoteUpdate) -> Note:
    """
    Changes only the fields sent: title, body or parent (a move)
    """

    return update_note(conn=conn, note_id=note_id, patch=patch)


@router.delete("/{note_id}", status_code=204)
def delete_note(conn: Conn, note_id: UUID) -> Response:
    """
    Deletes a note, or a folder with everything inside it
    """

    remove_note(conn=conn, note_id=note_id)

    return Response(status_code=204)
