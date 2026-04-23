from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dreamteams_exporter.entities.common.identifiers import ApplicationId, CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.participant.entity import Participant


@dataclass(slots=True, kw_only=True)
class Application:
    """A single application row."""

    id: ApplicationId
    competition_id: CompetitionId
    competition_name: str
    domains: list[str]
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None
    participant: Participant
