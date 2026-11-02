"""Create conversations and messages

Revision ID: 384c427fb4bd
Revises:
Create Date: 2026-11-02 15:27:14.788525

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "384c427fb4bd"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    One row per conversation, one row per message inside it
    """

    op.create_table(
        "conversations",
        sa.Column(
            "id",
            sa.Uuid,
            server_default=sa.text("uuidv7()"),
            primary_key=True,
        ),
        # The workspace folder, kept in ichiro's database: no foreign key
        # across databases. NULL = the root workspace
        sa.Column("folder_id", sa.Uuid, nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # The list of a workspace, most recent first
    op.create_index(
        "ix_conversations_folder_id_updated_at",
        "conversations",
        ["folder_id", "updated_at"],
    )

    op.create_table(
        "messages",
        # uuidv7 grows with time: ordering by id is the order of the talk
        sa.Column(
            "id",
            sa.Uuid,
            server_default=sa.text("uuidv7()"),
            primary_key=True,
        ),
        sa.Column(
            "conversation_id",
            sa.Uuid,
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.Text, nullable=False),
        # The content blocks of the Messages API, as they are sent back
        sa.Column("content", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_messages_role",
        ),
    )
    # The history of one conversation, in order
    op.create_index(
        "ix_messages_conversation_id_id",
        "messages",
        ["conversation_id", "id"],
    )


def downgrade() -> None:
    """
    Drops both tables, messages first (they point to conversations)
    """

    op.drop_table("messages")
    op.drop_table("conversations")
