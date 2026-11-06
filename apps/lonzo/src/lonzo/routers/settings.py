# Imports
from fastapi import APIRouter

from lonzo.schemas.settings import ModelOption, Settings, SettingsUpdate
from lonzo.services.settings import (
    get_settings,
    list_models,
    remove_key,
    save_settings,
)


# Global variables
router = APIRouter(prefix="/chat/settings")


# Code
@router.get("")
async def get_user_settings() -> Settings:
    """
    The settings of the user, without the key
    """

    return await get_settings()


@router.put("")
async def put_user_settings(body: SettingsUpdate) -> Settings:
    """
    Saves the settings; without api_key, the saved key stays
    """

    return await save_settings(update=body)


@router.get("/models")
async def get_models() -> list[ModelOption]:
    """
    The models the key of the user can use
    """

    return await list_models()


@router.delete("/key", status_code=204)
async def delete_key() -> None:
    """
    Forgets the key of the user
    """

    await remove_key()
