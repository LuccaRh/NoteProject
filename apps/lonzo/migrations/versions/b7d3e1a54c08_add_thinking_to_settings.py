"""Add thinking to settings

Revision ID: b7d3e1a54c08
Revises: 9b2f4d17c6e3
Create Date: 2026-11-06 00:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b7d3e1a54c08"
down_revision: str | Sequence[str] | None = "9b2f4d17c6e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    The kind of thinking of the user; who already saved stays without it,
    as lonzo always called the model
    """

    op.add_column(
        "settings",
        sa.Column(
            "thinking",
            sa.Text,
            nullable=False,
            server_default="disabled",
        ),
    )


def downgrade() -> None:
    """
    Back to no choice of thinking
    """

    op.drop_column("settings", "thinking")
