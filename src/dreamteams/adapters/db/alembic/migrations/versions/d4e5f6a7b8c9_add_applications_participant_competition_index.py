"""Add (participant_id, competition_id) index on applications

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-18 00:15:00.000000

"""
from alembic import op

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backs the NOT EXISTS anti-join in ExploreCompetitions:
    #   NOT EXISTS (SELECT 1 FROM applications
    #               WHERE competition_id = c.id AND participant_id = :pid)
    # The existing ix_applications_participant_id_created_at helps but the
    # planner still has to probe by (participant_id, competition_id) pair, which
    # this index serves directly as an index-only lookup.
    op.create_index(
        'ix_applications_participant_id_competition_id',
        'applications',
        ['participant_id', 'competition_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_applications_participant_id_competition_id', table_name='applications')
