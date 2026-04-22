"""Make competition team_size columns nullable

Revision ID: e8f3a2d1c4b9
Revises: d4e5f6a7b8c9
Create Date: 2026-04-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e8f3a2d1c4b9'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('competitions', 'max_team_size',
               existing_type=sa.Integer(),
               nullable=True)
    op.alter_column('competitions', 'min_team_size',
               existing_type=sa.Integer(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('competitions', 'min_team_size',
               existing_type=sa.Integer(),
               nullable=False)
    op.alter_column('competitions', 'max_team_size',
               existing_type=sa.Integer(),
               nullable=False)
