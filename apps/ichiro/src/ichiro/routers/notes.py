# Imports
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg.errors import UniqueViolation
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from ichiro.db import get_conn
from ichiro.errors.notes import (
    not_found,
    parent_inside_note,
    parent_not_folder,
    parent_not_found,
    title_taken,
)
from ichiro.schemas.notes import Note, NoteCreate, NoteUpdate


# Global variables
router = APIRouter(prefix="/notes")
Conn = Annotated[Connection, Depends(get_conn)]
COLUMNS = "id, parent_id, is_folder, title, body, created_at, updated_at"


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

    is_folder = conn.execute(
        text("SELECT is_folder FROM notes WHERE id = :id"),
        {"id": parent_id},
    ).scalar_one_or_none()

    if is_folder is None:
        raise parent_not_found()

    if not is_folder:
        raise parent_not_folder()

    # Check to see if note is being created (null id yet) or updated
    if note_id is None:
        return

    # folder cant be moved from outside to inside
    is_cycle = conn.execute(
        text(
            "WITH RECURSIVE ancestors AS ("
            " SELECT id, parent_id FROM notes WHERE id = :parent_id"
            " UNION"
            " SELECT n.id, n.parent_id FROM notes n"
            " JOIN ancestors a ON n.id = a.parent_id"
            ") SELECT EXISTS (SELECT 1 FROM ancestors WHERE id = :note_id)"
        ),
        {"parent_id": parent_id, "note_id": note_id},
    ).scalar_one()

    if is_cycle:
        raise parent_inside_note()


def integrity_error(error: IntegrityError) -> HTTPException:
    """
    The error for an insert or update the table refused: a title already
    in the folder, or a parent deleted in the meantime
    """

    if isinstance(error.orig, UniqueViolation):
        return title_taken()

    return parent_not_found()


@router.get("")
def list_notes(
    conn: Conn,
    parent_id: UUID | None = None,
    title: str | None = None,
) -> list[Note]:
    """
    Notes right inside parent_id (the root when none), folders first,
    then by title; only the ones with this title when one is given
    """

    rows = conn.execute(
        text(
            f"SELECT {COLUMNS} FROM notes"
            " WHERE parent_id IS NOT DISTINCT FROM CAST(:parent_id AS uuid)"
            " AND (CAST(:title AS text) IS NULL OR title = :title)"
            " ORDER BY is_folder DESC, title"
        ),
        {"parent_id": parent_id, "title": title},
    ).mappings()

    return [Note.model_validate(row) for row in rows]


@router.get("/{note_id}")
def get_note(conn: Conn, note_id: UUID) -> Note:
    """
    One note by id; 404 when it doesn't exist
    """

    row = conn.execute(
        text(f"SELECT {COLUMNS} FROM notes WHERE id = :id"),
        {"id": note_id},
    ).mappings().one_or_none()

    if row is None:
        raise not_found()

    return Note.model_validate(row)


@router.post("", status_code=201)
def create_note(conn: Conn, note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

    check_parent(conn=conn, parent_id=note.parent_id)

    try:
        row = conn.execute(
            text(
                "INSERT INTO notes (parent_id, is_folder, title, body)"
                " VALUES (:parent_id, :is_folder, :title, :body)"
                f" RETURNING {COLUMNS}"
            ),
            note.model_dump(),
        ).mappings().one()
    except IntegrityError as error:
        raise integrity_error(error=error)

    return Note.model_validate(row)


@router.patch("/{note_id}")
def update_note(conn: Conn, note_id: UUID, patch: NoteUpdate) -> Note:
    """
    Changes only the fields sent: title, body or parent (a move)
    """

    # Only the fields sent in the request: parent_id null moves to the root
    fields = patch.model_dump(exclude_unset=True)

    # cant update title or body to null
    if fields.get("title", "") is None or fields.get("body", "") is None:
        raise HTTPException(status_code=422, detail="title and body not null")

    # check if the new parent_id exists
    if "parent_id" in fields:
        check_parent(conn=conn, parent_id=fields["parent_id"], note_id=note_id)

    # Keys come from NoteUpdate, never from the client: safe in the SQL
    sets = "".join(f"{key} = :{key}, " for key in fields)

    try:
        row = conn.execute(
            text(
                f"UPDATE notes SET {sets}updated_at = now()"
                f" WHERE id = :id RETURNING {COLUMNS}"
            ),
            {**fields, "id": note_id},
        ).mappings().one_or_none()
    except IntegrityError as error:
        raise integrity_error(error=error)

    if row is None:
        raise not_found()

    return Note.model_validate(row)


@router.delete("/{note_id}", status_code=204)
def delete_note(conn: Conn, note_id: UUID) -> Response:
    """
    Deletes a note, or a folder with everything inside it
    """

    result = conn.execute(
        text("DELETE FROM notes WHERE id = :id RETURNING id"),
        {"id": note_id},
    )

    if result.one_or_none() is None:
        raise not_found()

    return Response(status_code=204)
