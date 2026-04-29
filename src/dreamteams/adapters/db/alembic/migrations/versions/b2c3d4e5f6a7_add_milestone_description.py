"""Add description to milestones

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-18 00:05:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'milestones',
        sa.Column('description', sa.String(length=300), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('milestones', 'description')
