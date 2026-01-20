from dataclasses import dataclass
from datetime import datetime

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.datetime_utils import normalize_datetime
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

        normalized_ts = normalize_datetime(self.timestamp)
        self.timestamp = normalized_ts


@dataclass(slots=True)
class MilestoneData:
    """Milestone creation data."""

    title: str
    timestamp: datetime


def milestone_factory(data: MilestoneData, clock: Clock) -> Milestone:
    """Create new milestone."""
    now = normalize_datetime(clock.now())
    normalized_ts = normalize_datetime(data.timestamp)

    if normalized_ts < now:
        raise InvalidCompetitionDataError(message="Milestone timestamp cannot be in past")

    return Milestone(normalized_ts, data.title)
