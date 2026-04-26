from uuid import uuid4

from dreamteams_common.clock import Clock
from dreamteams_exporter.entities.common.identifiers import CompetitionId, UserId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob
from dreamteams_exporter.entities.export_job.vo.status import JobStatus


def export_job_factory(
    *,
    user_id: UserId,
    competition_id: CompetitionId,
    application_status: ApplicationStatus | None,
    clock: Clock,
) -> ExportApplicationsJob:
    """Build a new export job in the pending state."""
    now = clock.now()
    return ExportApplicationsJob(
        id=uuid4(),
        user_id=user_id,
        competition_id=competition_id,
        application_status=application_status,
        status=JobStatus.pending(),
        file_url=None,
        created_at=now,
        finished_at=None,
    )
