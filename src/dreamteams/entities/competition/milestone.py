from dataclasses import dataclass
from datetime import datetime

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.datetime_utils import normalize_datetime
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass
class Milestone:
    """Competition milestone with timestamp, title, and optional description."""

    timestamp: datetime
    title: str
    description: str | None = None

    def __post_init__(self) -> None:
        """Normalize timestamp."""
        normalized_ts = normalize_datetime(self.timestamp)
        self.timestamp = normalized_ts


@dataclass(slots=True)
class MilestoneData:
    """Milestone creation data."""

    title: str
    timestamp: datetime
    description: str | None = None


def milestone_factory(data: MilestoneData, clock: Clock) -> Milestone:
    """Create new milestone."""
    now = normalize_datetime(clock.now())
    normalized_ts = normalize_datetime(data.timestamp)

    if normalized_ts <= now:
        raise InvalidCompetitionDataError(message="Milestone timestamp cannot be in past")

    return Milestone(timestamp=normalized_ts, title=data.title, description=data.description)
