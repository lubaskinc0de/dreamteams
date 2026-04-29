"""add application_forms table

Revision ID: d0ec760956a6
Revises: 91974e63fdd3
Create Date: 2026-04-13 22:05:07.792299

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd0ec760956a6'
down_revision = '91974e63fdd3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'application_forms',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('competition_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('competition_id', name='uq_application_forms_competition_id'),
    )


def downgrade() -> None:
    op.drop_table('application_forms')
