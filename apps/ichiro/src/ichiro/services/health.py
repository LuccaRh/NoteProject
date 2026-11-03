# Imports
from ichiro.db import transaction
from ichiro.repositories.health import select_one


# Code
def check_database() -> None:
    """
    Raises when the database is down
    """

    with transaction() as conn:
        select_one(conn=conn)
