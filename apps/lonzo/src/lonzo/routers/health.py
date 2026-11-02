# Imports
from fastapi import APIRouter


# Global variables
router = APIRouter()


# Code
@router.get("/health")
def health() -> dict[str, str]:
    """
    Answers ok while the service is up
    """

    return {"status": "ok"}
