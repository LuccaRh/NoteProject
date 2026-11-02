# Code
class MissingApiKey(Exception):
    """
    ANTHROPIC_API_KEY is not set, so no call to the model can go out
    """


class TitleTaken(Exception):
    """
    The folder already has a note or folder with that title (ichiro's 409)
    """


class FolderNotFound(Exception):
    """
    The folder asked for does not exist in ichiro
    """


class NotAFolder(Exception):
    """
    The id asked for is a note, not a folder
    """


class ConversationNotFound(Exception):
    """
    No conversation has the id asked for
    """
