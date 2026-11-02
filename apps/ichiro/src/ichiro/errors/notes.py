# Imports
from fastapi import HTTPException


# Code
def not_found() -> HTTPException:
    """
    404 for a note id that isn't in the table
    """

    return HTTPException(status_code=404, detail="note not found")


def parent_not_found() -> HTTPException:
    """
    422 for a parent_id that isn't in the table
    """

    return HTTPException(status_code=422, detail="parent not found")


def parent_not_folder() -> HTTPException:
    """
    422 for a parent that is a note, not a folder
    """

    return HTTPException(status_code=422, detail="parent is not a folder")


def parent_inside_note() -> HTTPException:
    """
    422 for a move that would put a folder inside itself
    """

    return HTTPException(
        status_code=422,
        detail="cannot move a folder inside itself",
    )
