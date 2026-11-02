"""Keep note titles unique inside a folder

Revision ID: 8e0077239938
Revises: e7dd73f8b32e
Create Date: 2026-11-02 04:04:38.482533

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8e0077239938'
down_revision: str | Sequence[str] | None = 'e7dd73f8b32e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # NULLS NOT DISTINCT: two notes with the same title at the root
    # (parent_id NULL) also collide
    op.execute(
        "ALTER TABLE notes ADD CONSTRAINT notes_parent_id_title_key"
        " UNIQUE NULLS NOT DISTINCT (parent_id, title)"
    )


def downgrade() -> None:
    op.drop_constraint("notes_parent_id_title_key", "notes")
