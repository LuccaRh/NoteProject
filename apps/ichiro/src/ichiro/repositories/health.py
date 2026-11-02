# Imports
from sqlalchemy import Connection, text


# Code
def select_one(conn: Connection) -> None:
    """
    Runs the smallest query, so a database that is down raises here
    """

    conn.execute(text("SELECT 1"))
