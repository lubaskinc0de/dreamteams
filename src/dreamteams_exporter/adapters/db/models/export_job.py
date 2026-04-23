from sqlalchemy import UUID, Column, DateTime, Enum, Index, Table, Text
from sqlalchemy.orm import composite

from dreamteams_exporter.adapters.db.models.base import mapper_registry
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob
from dreamteams_exporter.entities.export_job.vo.status import JobStatus, JobStatusKind


def _status_composite(kind: str, reason: str | None) -> JobStatus:
    """Composite factory: reconstructs the JobStatus VO from two stored columns."""
    return JobStatus(kind=JobStatusKind(kind), reason=reason)


def _status_decompose(status: JobStatus) -> tuple[str, str | None]:
    """Composite accessor: flattens the JobStatus VO back into two columns on write."""
    return (status.kind.value, status.reason)


export_job_table = Table(
    "export_jobs",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("competition_id", UUID(as_uuid=True), nullable=False),
    Column("application_status", Enum(ApplicationStatus, native_enum=False), nullable=False),
    Column("status_kind", Enum(JobStatusKind, native_enum=False), nullable=False),
    Column("status_reason", Text, nullable=True),
    Column("file_url", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("finished_at", DateTime(timezone=True), nullable=True),
    Index("ix_export_jobs_user_id_created_at", "user_id", "created_at"),
    Index("ix_export_jobs_status_kind", "status_kind"),
)


_status_property = composite(
    _status_composite,
    export_job_table.c.status_kind,
    export_job_table.c.status_reason,
)
_status_property._generated_composite_accessor = _status_decompose  # noqa: SLF001


mapper_registry.map_imperatively(
    ExportApplicationsJob,
    export_job_table,
    properties={"status": _status_property},
)
