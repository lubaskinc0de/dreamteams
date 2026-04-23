from dataclasses import dataclass
from datetime import datetime

from dreamteams_exporter.entities.common.identifiers import (
    CompetitionId,
    ExportJobId,
    UserId,
)
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus


@dataclass(slots=True, kw_only=True, frozen=True)
class ExportJobModel:
    """Read model for an export job."""

    id: ExportJobId
    user_id: UserId
    competition_id: CompetitionId
    application_status: ApplicationStatus
    status_kind: str
    status_reason: str | None
    file_url: str | None
    created_at: datetime
    finished_at: datetime | None
