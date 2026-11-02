# Code
class NoteNotFound(Exception):
    """
    The note id asked for isn't in the table
    """


class ParentNotFound(Exception):
    """
    The parent_id isn't in the table, or was deleted in the meantime
    """


class ParentNotAFolder(Exception):
    """
    The parent is a note, not a folder
    """


class ParentInsideNote(Exception):
    """
    The move would put a folder inside itself or one of its subfolders
    """


class TitleTaken(Exception):
    """
    Another note in the same folder already has this title
    """


class PathEmpty(Exception):
    """
    The path has no names, only slashes or nothing at all
    """


class FieldNull(Exception):
    """
    The update sent null for a field that can't be null
    """
