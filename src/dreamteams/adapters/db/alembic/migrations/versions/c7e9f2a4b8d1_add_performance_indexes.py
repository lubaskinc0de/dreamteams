"""Add performance indexes

Revision ID: c7e9f2a4b8d1
Revises: 5448829ba76d
Create Date: 2026-04-16 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c7e9f2a4b8d1'
down_revision = '5448829ba76d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pg_trgm extension required for word_similarity search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Priority 1: FK columns — PostgreSQL does not auto-index FK columns,
    # but these are hit on every authenticated request via selectin relationships.
    op.create_index('ix_auth_user_user_id', 'auth_user', ['user_id'])
    op.create_index('ix_organizer_user_id', 'organizer', ['user_id'])
    op.create_index('ix_participant_user_id', 'participants', ['user_id'])
    op.create_index('ix_milestones_competition_id', 'milestones', ['competition_id'])
    op.create_index('ix_competitions_organizer_id', 'competitions', ['organizer_id'])

    # Priority 2: Filtering + pagination queries
    op.create_index(
        'ix_applications_competition_id_created_at',
        'applications',
        ['competition_id', sa.text('created_at DESC')],
    )
    op.create_index(
        'ix_applications_participant_id_created_at',
        'applications',
        ['participant_id', sa.text('created_at DESC')],
    )
    op.create_index(
        'ix_applications_competition_id_status',
        'applications',
        ['competition_id', 'status'],
    )
    op.create_index(
        'ix_competitions_is_archived_organizer_id_created_at',
        'competitions',
        ['is_archived', 'organizer_id', 'created_at'],
    )
    op.create_index(
        'ix_organizer_invite_created_by_created_at',
        'organizer_invite',
        ['created_by', sa.text('created_at DESC')],
    )

    # Priority 3: Range queries for the active competitions filter
    # (registration_start < now AND registration_end > now)
    op.create_index(
        'ix_competitions_registration_dates',
        'competitions',
        ['registration_start', 'registration_end'],
    )

    # Priority 4: GIN trigram index for word_similarity(lower(title), search)
    op.execute(
        "CREATE INDEX ix_competitions_title_trgm "
        "ON competitions USING gin (lower(title) gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_competitions_title_trgm")
    op.drop_index('ix_competitions_registration_dates', table_name='competitions')
    op.drop_index('ix_organizer_invite_created_by_created_at', table_name='organizer_invite')
    op.drop_index('ix_competitions_is_archived_organizer_id_created_at', table_name='competitions')
    op.drop_index('ix_applications_competition_id_status', table_name='applications')
    op.drop_index('ix_applications_participant_id_created_at', table_name='applications')
    op.drop_index('ix_applications_competition_id_created_at', table_name='applications')
    op.drop_index('ix_competitions_organizer_id', table_name='competitions')
    op.drop_index('ix_milestones_competition_id', table_name='milestones')
    op.drop_index('ix_participant_user_id', table_name='participants')
    op.drop_index('ix_organizer_user_id', table_name='organizer')
    op.drop_index('ix_auth_user_user_id', table_name='auth_user')
