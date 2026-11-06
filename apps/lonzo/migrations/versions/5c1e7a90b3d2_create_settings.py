"""Create settings

Revision ID: 5c1e7a90b3d2
Revises: 0417cfe26c6f
Create Date: 2026-11-05 22:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5c1e7a90b3d2"
down_revision: str | Sequence[str] | None = "0417cfe26c6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The user of the request, set by db.transaction(); NULL when unset
CURRENT_USER = "nullif(current_setting('app.user_id', true), '')::uuid"


def upgrade() -> None:
    """
    One row of settings per user, only after they save, and row-level
    security so each user sees only their own
    """

    op.create_table(
        "settings",
        sa.Column(
            "user_id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text(CURRENT_USER),
        ),
        sa.Column("api_key", sa.LargeBinary, nullable=True),
        sa.Column("key_end", sa.Text, nullable=True),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("max_tokens", sa.Integer, nullable=False),
        sa.Column(
            "show_workspace",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # FORCE: lonzo owns the tables, and the owner skips the policies
    # without it
    op.execute(
        f"CREATE POLICY settings_owner ON settings"
        f" USING (user_id = {CURRENT_USER})"
        f" WITH CHECK (user_id = {CURRENT_USER})"
    )
    op.execute("ALTER TABLE settings ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE settings FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    """
    Back to no settings
    """

    op.drop_table("settings")
