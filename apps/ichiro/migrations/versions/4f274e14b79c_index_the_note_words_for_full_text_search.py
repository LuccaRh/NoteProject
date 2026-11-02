"""Index the note words for full-text search

Revision ID: 4f274e14b79c
Revises: 8e0077239938
Create Date: 2026-11-02 20:00:13.419766

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4f274e14b79c'
down_revision: str | Sequence[str] | None = '8e0077239938'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Index over the expression: the table gets no new column
    op.execute(
        "CREATE INDEX notes_search_idx ON notes"
        " USING GIN (to_tsvector('simple', title || ' ' || body))"
    )


def downgrade() -> None:
    op.drop_index("notes_search_idx", "notes")
