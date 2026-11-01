# Imports
from fastapi import HTTPException


# Code
# 404 for a note id that isn't in the table
def not_found() -> HTTPException:

    return HTTPException(status_code=404, detail="note not found")


# 422 for a parent_id that isn't in the table
def parent_not_found() -> HTTPException:

    return HTTPException(status_code=422, detail="parent not found")


# 422 for a parent that is a note, not a folder
def parent_not_folder() -> HTTPException:

    return HTTPException(status_code=422, detail="parent is not a folder")


# 422 for a move that would put a folder inside itself
def parent_inside_note() -> HTTPException:

    return HTTPException(
        status_code=422, detail="cannot move a folder inside itself"
    )
