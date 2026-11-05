# Imports
from uuid import UUID

from pydantic import BaseModel


# Code
class Login(BaseModel):
    """
    Email and password typed in the login form
    """

    email: str
    password: str


class Session(BaseModel):
    """
    The user a session cookie belongs to
    """

    user_id: UUID
