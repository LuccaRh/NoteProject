# Code
class MissingApiKey(Exception):
    """
    The user saved no key and ANTHROPIC_API_KEY is not set, so no call to
    the model can go out
    """


class InvalidApiKey(Exception):
    """
    The Anthropic API refused the key
    """


class InvalidSettings(Exception):
    """
    The model does not exist for the key, or allows fewer tokens
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
