"""Create notes

Revision ID: e7dd73f8b32e
Revises: 
Create Date: 2026-10-23 02:02:10.530222

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e7dd73f8b32e'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column(
            "id", 
            sa.Uuid, 
            server_default=sa.text("uuidv7()"), 
            primary_key=True
        ),
        # NULL = note at the root; deleting a folder deletes what is inside it
        
        sa.Column(
            "parent_id",
            sa.Uuid,
            sa.ForeignKey("notes.id", ondelete="CASCADE"),
            nullable=True,
        ),

        sa.Column(
            "is_folder",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False, server_default=""),
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


def downgrade() -> None:
    op.drop_table("notes")
