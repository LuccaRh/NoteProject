"""Add tool turns to settings

Revision ID: 9b2f4d17c6e3
Revises: 5c1e7a90b3d2
Create Date: 2026-11-05 23:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9b2f4d17c6e3"
down_revision: str | Sequence[str] | None = "5c1e7a90b3d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    The turns of the tool loop; who already saved starts with the limit
    that was fixed until now
    """

    op.add_column(
        "settings",
        sa.Column(
            "tools_max_turns",
            sa.Integer,
            nullable=False,
            server_default="20",
        ),
    )


def downgrade() -> None:
    """
    Back to the fixed limit
    """

    op.drop_column("settings", "tools_max_turns")
