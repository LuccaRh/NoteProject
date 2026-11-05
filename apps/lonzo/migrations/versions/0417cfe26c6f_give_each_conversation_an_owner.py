"""Give each conversation an owner

Revision ID: 0417cfe26c6f
Revises: 384c427fb4bd
Create Date: 2026-11-03 13:40:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import context, op


# revision identifiers, used by Alembic.
revision: str = "0417cfe26c6f"
down_revision: str | Sequence[str] | None = "384c427fb4bd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The user of the request, set by db.transaction(); NULL when unset
CURRENT_USER = "nullif(current_setting('app.user_id', true), '')::uuid"


def upgrade() -> None:
    """
    owner_id on the conversations, and row-level security so each user
    sees only their own conversations and the messages inside them
    """

    # The conversations already there go to the user given in
    # alembic -x owner=<user id from nujabes> upgrade head
    owner = context.get_x_argument(as_dictionary=True).get("owner")
    has_rows = op.get_bind().execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM conversations)")
    ).scalar_one()

    if has_rows and owner is None:
        raise RuntimeError(
            "conversations already exist: pass their owner with"
            " alembic -x owner=<user id> upgrade head"
        )

    op.add_column(
        "conversations",
        sa.Column("owner_id", sa.Uuid, nullable=True),
    )

    if has_rows:
        update = sa.text(
            "UPDATE conversations SET owner_id = CAST(:owner AS uuid)"
        )
        op.execute(update.bindparams(owner=owner))

    # A new conversation belongs to the user of the request
    op.alter_column(
        "conversations",
        "owner_id",
        nullable=False,
        server_default=sa.text(CURRENT_USER),
    )

    # The list of a workspace is now the list of one user's workspace
    op.drop_index("ix_conversations_folder_id_updated_at", "conversations")
    op.create_index(
        "ix_conversations_owner_id_folder_id_updated_at",
        "conversations",
        ["owner_id", "folder_id", "updated_at"],
    )

    # FORCE: lonzo owns the tables, and the owner skips the policies
    # without it
    op.execute(
        f"CREATE POLICY conversations_owner ON conversations"
        f" USING (owner_id = {CURRENT_USER})"
        f" WITH CHECK (owner_id = {CURRENT_USER})"
    )
    op.execute("ALTER TABLE conversations ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE conversations FORCE ROW LEVEL SECURITY")

    # A message goes with its conversation: the subquery already sees
    # only the conversations of the user
    op.execute(
        "CREATE POLICY messages_owner ON messages"
        " USING (EXISTS (SELECT 1 FROM conversations c"
        " WHERE c.id = conversation_id))"
    )
    op.execute("ALTER TABLE messages ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE messages FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    """
    Back to conversations without owner, seen by everyone
    """

    op.execute("ALTER TABLE messages NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE messages DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY messages_owner ON messages")
    op.execute("ALTER TABLE conversations NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE conversations DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY conversations_owner ON conversations")
    op.drop_index(
        "ix_conversations_owner_id_folder_id_updated_at",
        "conversations",
    )
    op.create_index(
        "ix_conversations_folder_id_updated_at",
        "conversations",
        ["folder_id", "updated_at"],
    )
    op.drop_column("conversations", "owner_id")
