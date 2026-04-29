"""Rename participant contact url to value.

Revision ID: c8f4a2d9b1e3
Revises: b4d9e2f7a6c1
Create Date: 2026-04-27 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "c8f4a2d9b1e3"
down_revision: str | None = "b4d9e2f7a6c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Rename participant contact storage column to value."""
    op.alter_column("participant_contacts", "url", new_column_name="value")


def downgrade() -> None:
    """Rename participant contact storage column back to url."""
    op.alter_column("participant_contacts", "value", new_column_name="url")
