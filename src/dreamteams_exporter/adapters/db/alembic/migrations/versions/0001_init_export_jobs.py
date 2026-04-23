"""Init export jobs table.

Revision ID: 0001_init_export_jobs
Revises:
Create Date: 2026-04-23 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.schema import CreateSchema, DropSchema

from dreamteams_exporter.adapters.db.config import EXPORTER_SCHEMA
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.export_job.vo.status import JobStatusKind

revision: str = "0001_init_export_jobs"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the exporter schema and the export_jobs table inside it."""
    op.execute(CreateSchema(EXPORTER_SCHEMA, if_not_exists=True))

    op.create_table(
        "export_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("competition_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "application_status",
            sa.Enum(ApplicationStatus, native_enum=False, name="application_status"),
            nullable=False,
        ),
        sa.Column(
            "status_kind",
            sa.Enum(JobStatusKind, native_enum=False, name="job_status_kind"),
            nullable=False,
        ),
        sa.Column("status_reason", sa.Text, nullable=True),
        sa.Column("file_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        schema=EXPORTER_SCHEMA,
    )
    op.create_index(
        "ix_export_jobs_user_id_created_at",
        "export_jobs",
        ["user_id", "created_at"],
        schema=EXPORTER_SCHEMA,
    )
    op.create_index(
        "ix_export_jobs_status_kind",
        "export_jobs",
        ["status_kind"],
        schema=EXPORTER_SCHEMA,
    )


def downgrade() -> None:
    """Drop the export_jobs table and the exporter schema."""
    op.drop_index("ix_export_jobs_status_kind", table_name="export_jobs", schema=EXPORTER_SCHEMA)
    op.drop_index("ix_export_jobs_user_id_created_at", table_name="export_jobs", schema=EXPORTER_SCHEMA)
    op.drop_table("export_jobs", schema=EXPORTER_SCHEMA)
    op.execute(DropSchema(EXPORTER_SCHEMA))
