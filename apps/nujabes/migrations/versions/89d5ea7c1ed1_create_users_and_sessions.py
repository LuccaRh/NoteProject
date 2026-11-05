"""Create users and sessions

Revision ID: 89d5ea7c1ed1
Revises:
Create Date: 2026-11-03 12:31:31.252154

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '89d5ea7c1ed1'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # crypt() hashes the passwords and digest() the session tokens
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # A user is added by hand for now:
    # INSERT INTO users (email, password_hash)
    # VALUES ('me@example.com', crypt('secret', gen_salt('bf')));
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Uuid,
            server_default=sa.text("uuidv7()"),
            primary_key=True,
        ),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Only the hash of the token is kept: a leaked table logs no one in
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.LargeBinary, primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now() + interval '30 days'"),
        ),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("users")
