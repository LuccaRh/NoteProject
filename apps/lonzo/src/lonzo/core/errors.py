# Code
class MissingApiKey(Exception):
    """
    The user saved no key, so no call to the model can go out
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


class NotAWorkspace(Exception):
    """
    The folder asked for has no .workspace
    """


class NotASkill(Exception):
    """
    The note asked for is not a skill of the person, or it is empty
    """


class SkillNotFound(Exception):
    """
    No published skill has the id asked for
    """
