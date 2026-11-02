# Imports
from sqlalchemy import Connection

from ichiro.repositories.health import select_one


# Code
def check_database(conn: Connection) -> None:
    """
    Raises when the database is down
    """

    select_one(conn=conn)
