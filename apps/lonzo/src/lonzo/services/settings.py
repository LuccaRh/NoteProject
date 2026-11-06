# Imports
from lonzo.core.cipher import decrypt, encrypt
from lonzo.core.connections import claude
from lonzo.core.db import transaction
from lonzo.core.errors import InvalidSettings, MissingApiKey
from lonzo.repositories.settings import (
    clear_key,
    select_settings,
    upsert_settings,
)
from lonzo.schemas.settings import (
    ModelOption,
    ModelSettings,
    Settings,
    SettingsUpdate,
    StoredSettings,
)


# Code
async def load_stored() -> StoredSettings:
    """
    The saved settings of the user, or the defaults when there are none
    """

    async with transaction() as conn:
        stored = await select_settings(conn=conn)

    return stored or StoredSettings()


def key_of(stored: StoredSettings) -> str | None:
    """
    The key of the user, decrypted; None when they saved none
    """

    if stored.api_key is None:
        return None

    return decrypt(token=stored.api_key)


def view_of(stored: StoredSettings) -> Settings:
    """
    The settings without the key, the only way they leave the service
    """

    return Settings(
        has_key=stored.api_key is not None,
        key_end=stored.key_end,
        model=stored.model,
        max_tokens=stored.max_tokens,
        tools_max_turns=stored.tools_max_turns,
        thinking=stored.thinking,
        show_workspace=stored.show_workspace,
    )


async def get_settings() -> Settings:
    """
    The settings of the user, for the front
    """

    return view_of(stored=await load_stored())


async def get_model_settings() -> ModelSettings:
    """
    The key, model and limit of a call to the model; MissingApiKey when
    the user saved no key
    """

    stored = await load_stored()
    api_key = key_of(stored=stored)

    if api_key is None:
        raise MissingApiKey("no Anthropic key: add one in the settings")

    return ModelSettings(
        api_key=api_key,
        model=stored.model,
        max_tokens=stored.max_tokens,
        tools_max_turns=stored.tools_max_turns,
        thinking=stored.thinking,
    )


async def list_models() -> list[ModelOption]:
    """
    The models the key of the user can use; none without a key
    """

    api_key = key_of(stored=await load_stored())

    if api_key is None:
        return []

    return await claude.list_models(api_key=api_key)


def check_model(update: SettingsUpdate, models: list[ModelOption]) -> None:
    """
    InvalidSettings when the model is not one of the key, when it allows
    fewer tokens than asked, or when it refuses that thinking
    """

    chosen = next((m for m in models if m.id == update.model), None)

    if chosen is None:
        raise InvalidSettings(f"unknown model: {update.model}")

    if chosen.max_tokens is not None and update.max_tokens > chosen.max_tokens:
        raise InvalidSettings(
            f"{chosen.name} allows at most {chosen.max_tokens} tokens"
        )

    if chosen.thinking and update.thinking not in chosen.thinking:
        raise InvalidSettings(
            f"{chosen.name} does not take thinking {update.thinking}"
        )


async def save_settings(update: SettingsUpdate) -> Settings:
    """
    Saves the settings; a new key, model, limit or thinking is checked with
    the API first (with a key to check it), so only showing the workspace
    needs no call to it. The key is saved encrypted
    """

    stored = await load_stored()
    api_key = update.api_key or key_of(stored=stored)
    changed = (
        update.api_key is not None
        or update.model != stored.model
        or update.max_tokens != stored.max_tokens
        or update.thinking != stored.thinking
    )

    if api_key is not None and changed:
        models = await claude.list_models(api_key=api_key)
        check_model(update=update, models=models)

    encrypted = None
    key_end = None

    if update.api_key is not None:
        encrypted = encrypt(text=update.api_key)
        key_end = update.api_key[-4:]

    async with transaction() as conn:
        saved = await upsert_settings(
            conn=conn,
            api_key=encrypted,
            key_end=key_end,
            model=update.model,
            max_tokens=update.max_tokens,
            tools_max_turns=update.tools_max_turns,
            thinking=update.thinking,
            show_workspace=update.show_workspace,
        )

    return view_of(stored=saved)


async def remove_key() -> None:
    """
    Forgets the key of the user
    """

    async with transaction() as conn:
        await clear_key(conn=conn)
