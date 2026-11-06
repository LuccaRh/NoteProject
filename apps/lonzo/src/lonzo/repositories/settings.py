# Imports
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from lonzo.schemas.settings import StoredSettings, Thinking


# Global variables
COLUMNS = (
    "api_key, key_end, model, max_tokens,"
    " tools_max_turns, thinking, show_workspace"
)


# Code
async def select_settings(conn: AsyncConnection) -> StoredSettings | None:
    """
    The settings of the user, whom the policy of the table picks; None
    when they never saved
    """

    result = await conn.execute(text(f"SELECT {COLUMNS} FROM settings"))
    row = result.mappings().one_or_none()

    if row is None:
        return None

    return StoredSettings.model_validate(row)


async def upsert_settings(
    conn: AsyncConnection,
    api_key: bytes | None,
    key_end: str | None,
    model: str,
    max_tokens: int,
    tools_max_turns: int,
    thinking: Thinking,
    show_workspace: bool,
) -> StoredSettings:
    """
    Creates the row of the user or updates it; a None key keeps the saved
    one
    """

    result = await conn.execute(
        text(
            f"INSERT INTO settings ({COLUMNS})"
            " VALUES (:api_key, :key_end, :model, :max_tokens,"
            " :tools_max_turns, :thinking, :show_workspace)"
            " ON CONFLICT (user_id) DO UPDATE SET"
            " api_key = COALESCE(EXCLUDED.api_key, settings.api_key),"
            " key_end = COALESCE(EXCLUDED.key_end, settings.key_end),"
            " model = EXCLUDED.model,"
            " max_tokens = EXCLUDED.max_tokens,"
            " tools_max_turns = EXCLUDED.tools_max_turns,"
            " thinking = EXCLUDED.thinking,"
            " show_workspace = EXCLUDED.show_workspace"
            f" RETURNING {COLUMNS}"
        ),
        {
            "api_key": api_key,
            "key_end": key_end,
            "model": model,
            "max_tokens": max_tokens,
            "tools_max_turns": tools_max_turns,
            "thinking": thinking,
            "show_workspace": show_workspace,
        },
    )

    return StoredSettings.model_validate(result.mappings().one())


async def clear_key(conn: AsyncConnection) -> None:
    """
    Forgets the key of the user, keeping their other settings
    """

    await conn.execute(
        text("UPDATE settings SET api_key = NULL, key_end = NULL"),
    )
