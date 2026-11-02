# Imports
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import Connection

from ichiro.db import get_conn
from ichiro.errors import (
    FieldNull,
    NoteNotFound,
    ParentInsideNote,
    ParentNotAFolder,
    ParentNotFound,
    PathEmpty,
)
from ichiro.repositories.notes import (
    delete_note,
    insert_note,
    select_by_path,
    select_children,
    select_is_folder,
    select_is_inside,
    select_note,
    select_tree,
    update_fields,
)
from ichiro.schemas.notes import Note, NoteCreate, NotePath, NoteUpdate


# Global variables
router = APIRouter(prefix="/notes")
Conn = Annotated[Connection, Depends(get_conn)]


# Code
def check_parent(
    conn: Connection,
    parent_id: UUID | None,
    note_id: UUID | None = None,
) -> None:
    """
    Refuse a parent that doesn't exist, isn't a folder or, when moving,
    is the note itself or one of its subfolders
    """

    # note/folder being created at root
    if parent_id is None:
        return

    is_folder = select_is_folder(conn=conn, note_id=parent_id)

    if is_folder is None:
        raise ParentNotFound("parent not found")

    if not is_folder:
        raise ParentNotAFolder("parent is not a folder")

    # Check to see if note is being created (null id yet) or updated
    if note_id is None:
        return

    # folder cant be moved from outside to inside
    if select_is_inside(conn=conn, folder_id=parent_id, note_id=note_id):
        raise ParentInsideNote("cannot move a folder inside itself")


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

    return select_children(conn=conn, parent_id=parent_id, title=title)


@router.get("/tree")
def get_tree(conn: Conn, parent_id: UUID | None = None) -> list[NotePath]:
    """
    Everything inside parent_id, at any depth, each with its path of
    titles from there; 404 when parent_id doesn't exist
    """

    if parent_id is not None:
        get_note(conn=conn, note_id=parent_id)

    return select_tree(conn=conn, parent_id=parent_id)


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

    names = [name for name in path.split("/") if name]

    if not names:
        raise PathEmpty("path is empty")

    note = select_by_path(conn=conn, names=names, parent_id=parent_id)

    if note is None:
        raise NoteNotFound("note not found")

    return note


@router.get("/{note_id}")
def get_note(conn: Conn, note_id: UUID) -> Note:
    """
    One note by id; 404 when it doesn't exist
    """

    note = select_note(conn=conn, note_id=note_id)

    if note is None:
        raise NoteNotFound("note not found")

    return note


@router.post("", status_code=201)
def post_note(conn: Conn, note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

    check_parent(conn=conn, parent_id=note.parent_id)

    return insert_note(conn=conn, note=note)


@router.patch("/{note_id}")
def patch_note(conn: Conn, note_id: UUID, patch: NoteUpdate) -> Note:
    """
    Changes only the fields sent: title, body or parent (a move)
    """

    # Only the fields sent in the request: parent_id null moves to the root
    fields = patch.model_dump(exclude_unset=True)

    # cant update title or body to null
    if fields.get("title", "") is None or fields.get("body", "") is None:
        raise FieldNull("title and body not null")

    # check if the new parent_id exists
    if "parent_id" in fields:
        check_parent(conn=conn, parent_id=fields["parent_id"], note_id=note_id)

    note = update_fields(conn=conn, note_id=note_id, fields=fields)

    if note is None:
        raise NoteNotFound("note not found")

    return note


@router.delete("/{note_id}", status_code=204)
def remove_note(conn: Conn, note_id: UUID) -> Response:
    """
    Deletes a note, or a folder with everything inside it
    """

    if not delete_note(conn=conn, note_id=note_id):
        raise NoteNotFound("note not found")

    return Response(status_code=204)
