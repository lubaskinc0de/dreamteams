"""add created_at to users

Revision ID: b4d9e2f7a6c1
Revises: a3c1f8b2e5d9
Create Date: 2026-04-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b4d9e2f7a6c1"
down_revision: str | None = "a3c1f8b2e5d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_created_at", "users", [sa.text("created_at DESC")])
    op.execute(
        "CREATE INDEX ix_organizer_name_trgm "
        "ON organizer USING gin (lower(organizer_name) gin_trgm_ops)",
    )
    op.execute(
        "CREATE INDEX ix_participants_full_name_trgm "
        "ON participants USING gin (lower(full_name) gin_trgm_ops)",
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_participants_full_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_organizer_name_trgm")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_column("users", "created_at")
