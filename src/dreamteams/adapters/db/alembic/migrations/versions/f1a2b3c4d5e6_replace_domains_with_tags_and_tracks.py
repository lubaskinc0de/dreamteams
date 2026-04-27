"""Replace domains with tags and tracks

Revision ID: f1a2b3c4d5e6
Revises: c8f4a2d9b1e3
Create Date: 2026-04-27 00:00:00.000000

"""
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "c8f4a2d9b1e3"
branch_labels = None
depends_on = None

_SEEDED_TAGS = [
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0001", "Python"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0002", "JavaScript"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0003", "TypeScript"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0004", "Java"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0005", "C#"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0006", "C++"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0007", "C"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0008", "Go"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0009", "Rust"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0010", "Kotlin"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0011", "Swift"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0012", "PHP"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0013", "Ruby"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0014", "Scala"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0015", "Dart"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0016", "SQL"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0017", "Frontend"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0018", "Backend"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0019", "Mobile Development"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0020", "Web Development"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0021", "Data Science"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0022", "Machine Learning"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0023", "Artificial Intelligence"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0024", "Computer Vision"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0025", "Natural Language Processing"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0026", "DevOps"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0027", "Cloud Computing"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0028", "Cybersecurity"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0029", "Databases"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0030", "Distributed Systems"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0031", "Algorithms"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0032", "Game Development"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0033", "Embedded Systems"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0034", "Blockchain"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0035", "UI/UX"),
    ("3f90df42-1875-4e1a-8b50-3c6d1a2a0036", "Product Management"),
]


def upgrade() -> None:
    competition_tags = op.create_table(
        "competition_tags",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("value", sa.String(length=100), nullable=False),
    )
    op.create_table(
        "competition_tag_links",
        sa.Column(
            "competition_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("competitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("competition_tags.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("competition_id", "tag_id"),
    )
    op.create_table(
        "competition_tracks",
        sa.Column(
            "competition_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("competitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("competition_id", "name"),
    )

    op.bulk_insert(
        competition_tags,
        [{"id": UUID(tag_id), "value": value} for tag_id, value in _SEEDED_TAGS],
    )

    op.add_column("applications", sa.Column("track_name", sa.String(length=100), nullable=True))
    op.execute(
        """
        INSERT INTO competition_tracks (competition_id, name)
        SELECT id, 'General'
        FROM competitions
        """,
    )
    op.execute("UPDATE applications SET track_name = 'General'")
    op.alter_column("applications", "track_name", nullable=False)

    op.execute("DROP INDEX IF EXISTS ix_competitions_domains_gin")
    op.drop_column("applications", "domains")
    op.drop_column("participants", "preferred_domains")
    op.drop_column("competitions", "domains")

    op.execute("CREATE UNIQUE INDEX ux_competition_tags_lower_value ON competition_tags (lower(value))")
    op.execute("CREATE INDEX ix_competition_tags_lower_value_id ON competition_tags (lower(value), id)")
    op.execute(
        "CREATE INDEX ix_competition_tags_value_trgm "
        "ON competition_tags USING gin (lower(value) gin_trgm_ops)",
    )
    op.create_index(
        "ix_competition_tag_links_tag_id_competition_id",
        "competition_tag_links",
        ["tag_id", "competition_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_competition_tag_links_tag_id_competition_id", table_name="competition_tag_links")
    op.execute("DROP INDEX IF EXISTS ix_competition_tags_value_trgm")
    op.execute("DROP INDEX IF EXISTS ix_competition_tags_lower_value_id")
    op.execute("DROP INDEX IF EXISTS ux_competition_tags_lower_value")

    op.add_column("competitions", sa.Column("domains", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("participants", sa.Column("preferred_domains", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("applications", sa.Column("domains", sa.ARRAY(sa.String()), nullable=True))
    op.execute("UPDATE competitions SET domains = ARRAY['BACKEND']")
    op.execute("UPDATE participants SET preferred_domains = ARRAY[]::varchar[]")
    op.execute("UPDATE applications SET domains = ARRAY['BACKEND']")
    op.alter_column("competitions", "domains", nullable=False)
    op.alter_column("participants", "preferred_domains", nullable=False)
    op.alter_column("applications", "domains", nullable=False)
    op.execute("CREATE INDEX ix_competitions_domains_gin ON competitions USING gin (domains)")

    op.drop_column("applications", "track_name")
    op.drop_table("competition_tracks")
    op.drop_table("competition_tag_links")
    op.drop_table("competition_tags")
