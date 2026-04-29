"""add applications table

Revision ID: 2a9f8e3c1b7d
Revises: d0ec760956a6
Create Date: 2026-04-13 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '2a9f8e3c1b7d'
down_revision = 'd0ec760956a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('participant_id', sa.UUID(), nullable=False),
        sa.Column('competition_id', sa.UUID(), nullable=False),
        sa.Column(
            'domains',
            sa.ARRAY(sa.Enum('frontend', 'mobile', 'backend', 'ai', 'devops', name='domain', native_enum=False)),
            nullable=False,
        ),
        sa.Column(
            'status',
            sa.Enum('pending', 'accepted', 'rejected', name='applicationstatus', native_enum=False),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('form_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('participant_id', 'competition_id', name='uq_applications_participant_competition'),
    )


def downgrade() -> None:
    op.drop_table('applications')
