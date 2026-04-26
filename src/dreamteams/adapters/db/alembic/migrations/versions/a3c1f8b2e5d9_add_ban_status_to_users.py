"""add ban status to users

Revision ID: a3c1f8b2e5d9
Revises: e8f3a2d1c4b9
Create Date: 2026-04-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3c1f8b2e5d9"
down_revision: str | None = "e8f3a2d1c4b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("blocked_reason", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("blocked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_users_is_blocked",
        "users",
        ["id"],
        postgresql_where=sa.text("is_blocked = true"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_is_blocked", table_name="users")
    op.drop_column("users", "blocked_at")
    op.drop_column("users", "blocked_reason")
    op.drop_column("users", "is_blocked")
