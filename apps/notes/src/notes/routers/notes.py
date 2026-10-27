# Imports
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from notes.db import get_conn
from notes.errors.notes import (
    not_found,
    parent_inside_note,
    parent_not_folder,
    parent_not_found,
)
from notes.schemas.notes import Note, NoteCreate, NoteUpdate


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


@router.get("")
def list_notes(conn: Conn, parent_id: UUID | None = None) -> list[Note]:

    rows = conn.execute(
        text(
            f"SELECT {COLUMNS} FROM notes"
            " WHERE parent_id IS NOT DISTINCT FROM CAST(:parent_id AS uuid)"
            " ORDER BY is_folder DESC, title"
        ),
        {"parent_id": parent_id},
    ).mappings()

    return [Note.model_validate(row) for row in rows]


@router.get("/{note_id}")
def get_note(conn: Conn, note_id: UUID) -> Note:

    row = conn.execute(
        text(f"SELECT {COLUMNS} FROM notes WHERE id = :id"),
        {"id": note_id},
    ).mappings().one_or_none()

    if row is None:
        raise not_found()

    return Note.model_validate(row)


@router.post("", status_code=201)
def create_note(conn: Conn, note: NoteCreate) -> Note:

    check_parent(conn, note.parent_id)

    try:
        row = conn.execute(
            text(
                "INSERT INTO notes (parent_id, is_folder, title, body)"
                " VALUES (:parent_id, :is_folder, :title, :body)"
                f" RETURNING {COLUMNS}"
            ),
            note.model_dump(),
        ).mappings().one()
    except IntegrityError:
        raise parent_not_found()

    return Note.model_validate(row)


@router.patch("/{note_id}")
def update_note(conn: Conn, note_id: UUID, patch: NoteUpdate) -> Note:

    # Only the fields sent in the request: parent_id null moves to the root
    fields = patch.model_dump(exclude_unset=True)

    # cant update title or body to null
    if fields.get("title", "") is None or fields.get("body", "") is None:
        raise HTTPException(status_code=422, detail="title and body not null")

    # check if the new parent_id exists
    if "parent_id" in fields:
        check_parent(conn, fields["parent_id"], note_id)

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
    except IntegrityError:
        raise parent_not_found()

    if row is None:
        raise not_found()

    return Note.model_validate(row)


@router.delete("/{note_id}", status_code=204)
def delete_note(conn: Conn, note_id: UUID) -> Response:

    result = conn.execute(
        text("DELETE FROM notes WHERE id = :id RETURNING id"),
        {"id": note_id},
    )

    if result.one_or_none() is None:
        raise not_found()

    return Response(status_code=204)
