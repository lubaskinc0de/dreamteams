from dataclasses import dataclass
from datetime import datetime

from dreamteams_common.clock import Clock
from dreamteams_exporter.entities.common.identifiers import (
    CompetitionId,
    ExportJobId,
    UserId,
)
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.errors.job import InvalidJobStatusTransitionError
from dreamteams_exporter.entities.export_job.vo.status import JobStatus, JobStatusKind


@dataclass(slots=True, kw_only=True)
class ExportApplicationsJob:
    """Aggregate root for a single Excel-export request."""

    id: ExportJobId
    user_id: UserId
    competition_id: CompetitionId
    application_status: ApplicationStatus
    status: JobStatus
    file_url: str | None
    created_at: datetime
    finished_at: datetime | None

    def mark_success(self, file_url: str, clock: Clock) -> None:
        """Transitions a pending job to success with the resulting file URL."""
        if self.status.kind is not JobStatusKind.PENDING:
            raise InvalidJobStatusTransitionError(
                message=f"Cannot mark success from status {self.status.kind}",
            )
        self.status = JobStatus.success()
        self.file_url = file_url
        self.finished_at = clock.now()

    def mark_failed(self, reason: str, clock: Clock) -> None:
        """Transitions a pending job to failed with the given reason."""
        if self.status.kind is not JobStatusKind.PENDING:
            raise InvalidJobStatusTransitionError(
                message=f"Cannot mark failed from status {self.status.kind}",
            )
        self.status = JobStatus.failed(reason)
        self.finished_at = clock.now()
