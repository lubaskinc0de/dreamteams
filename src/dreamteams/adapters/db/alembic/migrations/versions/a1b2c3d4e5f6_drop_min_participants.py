"""Drop min_participants from competitions

Revision ID: a1b2c3d4e5f6
Revises: c7e9f2a4b8d1
Create Date: 2026-04-18 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'a1b2c3d4e5f6'
down_revision = 'c7e9f2a4b8d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('competitions', 'min_participants')


def downgrade() -> None:
    op.add_column(
        'competitions',
        sa.Column('min_participants', sa.Integer(), nullable=False, server_default='1'),
    )
    op.alter_column('competitions', 'min_participants', server_default=None)