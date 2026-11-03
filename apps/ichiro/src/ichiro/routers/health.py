# Imports
from fastapi import APIRouter

from ichiro.services.health import check_database


# Global variables
router = APIRouter()


# Code
@router.get("/health")
def health() -> dict[str, str]:
    """
    Answers ok while the service and its database are up
    """

    check_database()

    return {"status": "ok"}
