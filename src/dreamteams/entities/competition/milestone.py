from dataclasses import dataclass
from datetime import UTC, datetime

from dreamteams.entities.competition.schedule import normalize_datetime
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass
class Milestone:
    """Competition milestone with timestamp and title."""

    timestamp: datetime
    title: str

    def __post_init__(self) -> None:
        """Validate milestone data and normalize timestamp."""
        if not self.title or not self.title.strip():
            raise InvalidCompetitionDataError(message="Milestone title must not be empty")

        now = normalize_datetime(datetime.now(tz=UTC))
        normalized_ts = normalize_datetime(self.timestamp)

        if normalized_ts < now:
            raise InvalidCompetitionDataError(message="Milestone timestamp cannot be in past")

        self.timestamp = normalized_ts
