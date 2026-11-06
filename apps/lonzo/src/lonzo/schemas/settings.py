# Imports
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


# Global variables
ApiKey = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


# Code
class StoredSettings(BaseModel):
    """
    The settings as the table keeps them; the defaults are those of who
    never saved
    """

    api_key: bytes | None = None
    key_end: str | None = None
    model: str = "claude-haiku-5-5"
    max_tokens: int = 64000
    show_workspace: bool = False


class Settings(BaseModel):
    """
    The settings the front sees: of the key, only its end
    """

    has_key: bool
    key_end: str | None
    model: str
    max_tokens: int
    show_workspace: bool


class SettingsUpdate(BaseModel):
    """
    What the front saves; without api_key, the saved key stays
    """

    model: str = Field(min_length=1)
    max_tokens: int = Field(gt=0)
    show_workspace: bool
    api_key: ApiKey | None = None


class ModelSettings(BaseModel):
    """
    What a call to the model needs, with the key already decrypted
    """

    api_key: str
    model: str
    max_tokens: int


class ModelOption(BaseModel):
    """
    A model the key can use, with its limit of tokens when the API says it
    """

    id: str
    name: str
    max_tokens: int | None
