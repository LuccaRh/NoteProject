# Imports
from typing import Any
from uuid import UUID

from psycopg.errors import UniqueViolation
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from ichiro.errors import ParentNotFound, TitleTaken
from ichiro.schemas.notes import Note, NoteCreate, NoteMatch, NotePath


# Global variables
COLUMNS = "id, parent_id, is_folder, title, body, created_at, updated_at"


# Code
def integrity_error(error: IntegrityError) -> Exception:
    """
    The error for an insert or update the table refused: a title already
    in the folder, or a parent deleted in the meantime
    """

    if isinstance(error.orig, UniqueViolation):
        return TitleTaken("title already in folder")

    return ParentNotFound("parent not found")


def select_is_folder(conn: Connection, note_id: UUID) -> bool | None:
    """
    Whether the note is a folder; None when it doesn't exist
    """

    return conn.execute(
        text("SELECT is_folder FROM notes WHERE id = :id"),
        {"id": note_id},
    ).scalar_one_or_none()


def select_is_inside(conn: Connection, folder_id: UUID, note_id: UUID) -> bool:
    """
    Whether folder_id is note_id itself or somewhere inside it, walking
    up the parents of folder_id
    """

    is_inside: bool = conn.execute(
        text(
            "WITH RECURSIVE ancestors AS ("
            " SELECT id, parent_id FROM notes WHERE id = :folder_id"
            " UNION"
            " SELECT n.id, n.parent_id FROM notes n"
            " JOIN ancestors a ON n.id = a.parent_id"
            ") SELECT EXISTS (SELECT 1 FROM ancestors WHERE id = :note_id)"
        ),
        {"folder_id": folder_id, "note_id": note_id},
    ).scalar_one()

    return is_inside


def select_children(
    conn: Connection,
    parent_id: UUID | None,
    title: str | None,
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


def select_tree(conn: Connection, parent_id: UUID | None) -> list[NotePath]:
    """
    Everything inside parent_id (the root when none), at any depth, each
    with its path of titles from there, in the order of a file tree
    """

    rows = conn.execute(
        text(
            "WITH RECURSIVE tree AS ("
            " SELECT id, is_folder, ARRAY[title] AS names FROM notes"
            " WHERE parent_id IS NOT DISTINCT FROM CAST(:parent_id AS uuid)"
            " UNION ALL"
            " SELECT n.id, n.is_folder, t.names || n.title FROM notes n"
            " JOIN tree t ON n.parent_id = t.id"
            ") SELECT id, is_folder, array_to_string(names, '/') AS path"
            " FROM tree ORDER BY names"
        ),
        {"parent_id": parent_id},
    ).mappings()

    return [NotePath.model_validate(row) for row in rows]


def select_by_path(
    conn: Connection,
    names: list[str],
    parent_id: UUID | None,
) -> Note | None:
    """
    The note at a list of titles from parent_id (the root when none),
    walked down one name per level in one query; None when a name on
    the way is missing
    """

    row = conn.execute(
        text(
            "WITH RECURSIVE walk AS ("
            " SELECT id, 1 AS depth FROM notes"
            " WHERE parent_id IS NOT DISTINCT FROM CAST(:parent_id AS uuid)"
            " AND title = (CAST(:names AS text[]))[1]"
            " UNION ALL"
            " SELECT n.id, w.depth + 1 FROM notes n"
            " JOIN walk w ON n.parent_id = w.id"
            " WHERE n.title = (CAST(:names AS text[]))[w.depth + 1]"
            f") SELECT {COLUMNS} FROM notes WHERE id = ("
            " SELECT id FROM walk"
            " WHERE depth = cardinality(CAST(:names AS text[])))"
        ),
        {"parent_id": parent_id, "names": names},
    ).mappings().one_or_none()

    if row is None:
        return None

    return Note.model_validate(row)


def select_matches(
    conn: Connection,
    query: str,
    parent_id: UUID | None,
) -> list[NoteMatch]:
    """
    Notes (not folders) whose title or body has the words of query, by
    title; only the ones inside parent_id, at any depth, when one is given
    """

    # Same expression as notes_search_idx, or Postgres reads every row
    rows = conn.execute(
        text(
            "WITH RECURSIVE tree AS ("
            " SELECT id FROM notes WHERE parent_id = :parent_id"
            " UNION ALL"
            " SELECT n.id FROM notes n JOIN tree t ON n.parent_id = t.id"
            ") SELECT id, title FROM notes"
            " WHERE NOT is_folder"
            " AND to_tsvector('simple', title || ' ' || body)"
            " @@ websearch_to_tsquery('simple', :query)"
            " AND (CAST(:parent_id AS uuid) IS NULL"
            " OR id IN (SELECT id FROM tree))"
            " ORDER BY title"
        ),
        {"query": query, "parent_id": parent_id},
    ).mappings()

    return [NoteMatch.model_validate(row) for row in rows]


def select_note(conn: Connection, note_id: UUID) -> Note | None:
    """
    One note by id; None when it doesn't exist
    """

    row = conn.execute(
        text(f"SELECT {COLUMNS} FROM notes WHERE id = :id"),
        {"id": note_id},
    ).mappings().one_or_none()

    if row is None:
        return None

    return Note.model_validate(row)


def insert_note(conn: Connection, note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

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


def update_fields(
    conn: Connection,
    note_id: UUID,
    fields: dict[str, Any],
) -> Note | None:
    """
    Writes the given columns and the new updated_at; None when the note
    doesn't exist
    """

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
        return None

    return Note.model_validate(row)


def delete_note(conn: Connection, note_id: UUID) -> bool:
    """
    Deletes a note, or a folder with everything inside it; False when
    it doesn't exist
    """

    result = conn.execute(
        text("DELETE FROM notes WHERE id = :id RETURNING id"),
        {"id": note_id},
    )

    return result.one_or_none() is not None
