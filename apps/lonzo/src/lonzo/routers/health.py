# Imports
from fastapi import APIRouter


# Global variables
router = APIRouter()


# Code
@router.get("/health")
def health() -> dict[str, str]:

    return {"status": "ok"}
