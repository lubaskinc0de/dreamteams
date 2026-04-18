"""Add GIN index on competitions.domains for explore overlap filter

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-18 00:10:00.000000

"""
from alembic import op

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # GIN index supporting the `domains && ARRAY[...]` overlap filter used by
    # ExploreCompetitions; without it the explore endpoint falls back to a seq scan
    # whenever the `domains` filter is provided.
    op.execute("CREATE INDEX ix_competitions_domains_gin ON competitions USING gin (domains)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_competitions_domains_gin")
