"""Create skills

Revision ID: c4e8a2f16d90
Revises: b7d3e1a54c08
Create Date: 2026-11-06 10:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c4e8a2f16d90"
down_revision: str | Sequence[str] | None = "b7d3e1a54c08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The user of the request, set by db.transaction(); NULL when unset
CURRENT_USER = "nullif(current_setting('app.user_id', true), '')::uuid"


def upgrade() -> None:
    """
    The published skills: any logged user reads them, only the owner
    writes; note_id is the note it came from, in the ichiro database
    """

    op.create_table(
        "skills",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuidv7()"),
        ),
        sa.Column(
            "user_id",
            sa.Uuid,
            nullable=False,
            server_default=sa.text(CURRENT_USER),
        ),
        sa.Column("note_id", sa.Uuid, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.UniqueConstraint("user_id", "note_id"),
    )

    # FORCE: lonzo owns the tables, and the owner skips the policies
    # without it
    op.execute(
        f"CREATE POLICY skills_read ON skills FOR SELECT"
        f" USING ({CURRENT_USER} IS NOT NULL)"
    )
    op.execute(
        f"CREATE POLICY skills_owner ON skills"
        f" USING (user_id = {CURRENT_USER})"
        f" WITH CHECK (user_id = {CURRENT_USER})"
    )
    op.execute("ALTER TABLE skills ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE skills FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    """
    Back to no skills table
    """

    op.drop_table("skills")
