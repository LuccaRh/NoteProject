"""Give each note an owner

Revision ID: cb9bed2be48a
Revises: 4f274e14b79c
Create Date: 2026-11-03 13:05:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import context, op


# revision identifiers, used by Alembic.
revision: str = 'cb9bed2be48a'
down_revision: str | Sequence[str] | None = '4f274e14b79c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The user of the request, set by db.transaction(); NULL when unset
CURRENT_USER = "nullif(current_setting('app.user_id', true), '')::uuid"


def upgrade() -> None:
    # The notes already there go to the user given in
    # alembic -x owner=<user id from nujabes> upgrade head
    owner = context.get_x_argument(as_dictionary=True).get("owner")
    has_notes = op.get_bind().execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM notes)")
    ).scalar_one()

    if has_notes and owner is None:
        raise RuntimeError(
            "notes already exist: pass their owner with"
            " alembic -x owner=<user id> upgrade head"
        )

    op.add_column("notes", sa.Column("owner_id", sa.Uuid, nullable=True))

    if has_notes:
        update = sa.text("UPDATE notes SET owner_id = CAST(:owner AS uuid)")
        op.execute(update.bindparams(owner=owner))

    # A new note belongs to the user of the request: INSERTs stay the same
    op.alter_column(
        "notes",
        "owner_id",
        nullable=False,
        server_default=sa.text(CURRENT_USER),
    )
    op.create_index("notes_owner_id_idx", "notes", ["owner_id"])

    # Titles are unique inside a folder of each user, not across users
    op.drop_constraint("notes_parent_id_title_key", "notes")
    op.execute(
        "ALTER TABLE notes ADD CONSTRAINT notes_owner_id_parent_id_title_key"
        " UNIQUE NULLS NOT DISTINCT (owner_id, parent_id, title)"
    )

    # Each query sees and writes only the notes of the request's user;
    # FORCE applies it to the table owner too
    op.execute(
        f"CREATE POLICY notes_owner ON notes"
        f" USING (owner_id = {CURRENT_USER})"
        f" WITH CHECK (owner_id = {CURRENT_USER})"
    )
    op.execute("ALTER TABLE notes ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE notes FORCE ROW LEVEL SECURITY")

    # ichiro connects as this user (postgres/init), never a superuser
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON notes TO ichiro")


def downgrade() -> None:
    op.execute("REVOKE ALL ON notes FROM ichiro")
    op.execute("ALTER TABLE notes NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE notes DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY notes_owner ON notes")
    op.drop_constraint("notes_owner_id_parent_id_title_key", "notes")
    op.execute(
        "ALTER TABLE notes ADD CONSTRAINT notes_parent_id_title_key"
        " UNIQUE NULLS NOT DISTINCT (parent_id, title)"
    )
    op.drop_index("notes_owner_id_idx", "notes")
    op.drop_column("notes", "owner_id")
