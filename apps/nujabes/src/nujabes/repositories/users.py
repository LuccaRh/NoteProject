# Imports
from uuid import UUID

from sqlalchemy import Connection, text


# Code
def select_user_id(conn: Connection, email: str, password: str) -> UUID | None:
    """
    Id of the user with this email and password; None when either is
    wrong (crypt() with the stored hash as salt gives the hash back only
    for the right password)
    """

    return conn.execute(
        text(
            "SELECT id FROM users WHERE email = :email"
            " AND password_hash = crypt(:password, password_hash)"
        ),
        {"email": email, "password": password},
    ).scalar_one_or_none()
