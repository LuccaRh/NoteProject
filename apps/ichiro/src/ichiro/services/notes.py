# Imports
from uuid import UUID

from sqlalchemy import Connection

from ichiro.db import transaction
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
    select_matches,
    select_note,
    select_path,
    select_title_matches,
    select_tree,
    update_fields,
)
from ichiro.schemas.notes import (
    Note,
    NoteCreate,
    NoteMatch,
    NotePath,
    NoteUpdate,
    TitleMatch,
)


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


def load_note(conn: Connection, note_id: UUID) -> Note:
    """
    One note by id, inside the transaction of conn; NoteNotFound when it
    doesn't exist
    """

    note = select_note(conn=conn, note_id=note_id)

    if note is None:
        raise NoteNotFound("note not found")

    return note


def list_notes(parent_id: UUID | None, title: str | None) -> list[Note]:
    """
    Notes right inside parent_id (the root when none), folders first,
    then by title; only the ones with this title when one is given
    """

    with transaction() as conn:
        return select_children(conn=conn, parent_id=parent_id, title=title)


def list_tree(parent_id: UUID | None) -> list[NotePath]:
    """
    Everything inside parent_id (the root when none), at any depth, each
    with its path of titles from there, in the order of a file tree;
    NoteNotFound when parent_id doesn't exist
    """

    with transaction() as conn:

        if parent_id is not None:
            load_note(conn=conn, note_id=parent_id)

        return select_tree(conn=conn, parent_id=parent_id)


def search_notes(query: str, parent_id: UUID | None) -> list[NoteMatch]:
    """
    Notes (not folders) whose title or body has the words of query, by
    title, inside parent_id when one is given; NoteNotFound when
    parent_id doesn't exist
    """

    with transaction() as conn:

        if parent_id is not None:
            load_note(conn=conn, note_id=parent_id)

        return select_matches(conn=conn, query=query, parent_id=parent_id)


def search_titles(
    text_in_title: str,
    parent_id: UUID | None,
) -> list[TitleMatch]:
    """
    Notes and folders whose title contains the text, by title, inside
    parent_id when one is given; NoteNotFound when parent_id doesn't exist
    """

    with transaction() as conn:

        if parent_id is not None:
            load_note(conn=conn, note_id=parent_id)

        return select_title_matches(
            conn=conn,
            text_in_title=text_in_title,
            parent_id=parent_id,
        )


def find_by_path(path: str, parent_id: UUID | None) -> Note:
    """
    The note at a path of titles (a/b/c) from parent_id (the root when
    none); NoteNotFound when a name on the way is missing
    """

    names = [name for name in path.split("/") if name]

    if not names:
        raise PathEmpty("path is empty")

    with transaction() as conn:
        note = select_by_path(conn=conn, names=names, parent_id=parent_id)

    if note is None:
        raise NoteNotFound("note not found")

    return note


def find_note(note_id: UUID) -> Note:
    """
    One note by id; NoteNotFound when it doesn't exist
    """

    with transaction() as conn:
        return load_note(conn=conn, note_id=note_id)


def find_path(note_id: UUID) -> NotePath:
    """
    A note with its path of titles from the root; NoteNotFound when it
    doesn't exist
    """

    with transaction() as conn:
        note = load_note(conn=conn, note_id=note_id)
        path = select_path(conn=conn, note_id=note_id)

    return NotePath(id=note.id, path=path, is_folder=note.is_folder)


def create_note(note: NoteCreate) -> Note:
    """
    Saves a new note or folder and returns it as the table keeps it
    """

    with transaction() as conn:
        check_parent(conn=conn, parent_id=note.parent_id)

        return insert_note(conn=conn, note=note)


def update_note(note_id: UUID, patch: NoteUpdate) -> Note:
    """
    Changes only the fields sent: title, body or parent (a move)
    """

    # Only the fields sent in the request: parent_id null moves to the root
    fields = patch.model_dump(exclude_unset=True)

    # cant update title or body to null
    if fields.get("title", "") is None or fields.get("body", "") is None:
        raise FieldNull("title and body not null")

    with transaction() as conn:

        # check if the new parent_id exists
        if "parent_id" in fields:
            check_parent(
                conn=conn,
                parent_id=fields["parent_id"],
                note_id=note_id,
            )

        note = update_fields(conn=conn, note_id=note_id, fields=fields)

    if note is None:
        raise NoteNotFound("note not found")

    return note


def remove_note(note_id: UUID) -> None:
    """
    Deletes a note, or a folder with everything inside it
    """

    with transaction() as conn:
        deleted = delete_note(conn=conn, note_id=note_id)

    if not deleted:
        raise NoteNotFound("note not found")
