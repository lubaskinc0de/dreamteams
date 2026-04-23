from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams_exporter.adapters.db.models.export_job import export_job_table
from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob


class SAExportJobGateway(ExportJobGateway):
    """SQLAlchemy-backed implementation of ExportJobGateway, scoped to the exporter schema."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, job_id: ExportJobId) -> ExportApplicationsJob | None:
        """Loads the mutable aggregate so the interactor can mark success / failure."""
        result = await self._session.execute(
            select(ExportApplicationsJob).where(export_job_table.c.id == job_id),
        )

        return result.scalar_one_or_none()

    @override
    async def read(self, job_id: ExportJobId) -> ExportJobModel | None:
        """Returns the read model for the given job, or None when the row does not exist."""
        result = await self._session.execute(
            select(
                export_job_table.c.id,
                export_job_table.c.user_id,
                export_job_table.c.competition_id,
                export_job_table.c.application_status,
                export_job_table.c.status_kind,
                export_job_table.c.status_reason,
                export_job_table.c.file_url,
                export_job_table.c.created_at,
                export_job_table.c.finished_at,
            ).where(export_job_table.c.id == job_id),
        )

        row = result.one_or_none()
        if row is None:
            return None

        return ExportJobModel(
            id=row.id,
            user_id=row.user_id,
            competition_id=row.competition_id,
            application_status=row.application_status,
            status_kind=row.status_kind.value,
            status_reason=row.status_reason,
            file_url=row.file_url,
            created_at=row.created_at,
            finished_at=row.finished_at,
        )
