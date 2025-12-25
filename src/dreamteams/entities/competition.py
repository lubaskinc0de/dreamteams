from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto

from dreamteams.entities.base import Entity
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.errors.competition import InvalidCompetitionDataError

type Banner = str


class CompetitionFormat(StrEnum):
    """Format in which a competition is conducted."""

    ONLINE = auto()
    OFFLINE = auto()
    HYBRID = auto()


@dataclass(frozen=True, slots=True)
class ParticipantLimits:
    """Participant limits with minimum and maximum values."""

    max: int
    min: int

    def __post_init__(self) -> None:
        """Validate participant limits."""
        if self.max <= 0:
            raise InvalidCompetitionDataError(message="Max participants must be greater than 0")

        if self.min > self.max:
            raise InvalidCompetitionDataError(message="Min participants must be less than or equal to max participants")


@dataclass(frozen=True, slots=True)
class TeamSizeRange:
    """Team size range with minimum and maximum values."""

    max: int
    min: int

    def __post_init__(self) -> None:
        """Validate team size range."""
        if self.min < 1:
            raise InvalidCompetitionDataError(message="Min team size must be at least 1")

        if self.max <= 0:
            raise InvalidCompetitionDataError(message="Max team size must be greater than 0")

        if self.min > self.max:
            raise InvalidCompetitionDataError(message="Min team size must be less than or equal to max team size")


@dataclass(frozen=True, slots=True)
class CompetitionSchedule:
    """Competition schedule with dates and registration period."""

    competition_start: datetime
    competition_end: datetime
    registration_start: datetime
    registration_end: datetime

    def __post_init__(self) -> None:
        """Validate schedule dates."""
        if self.competition_end <= self.competition_start:
            raise InvalidCompetitionDataError(message="End date must be after start date")

        if self.registration_start >= self.registration_end:
            raise InvalidCompetitionDataError(message="Registration start date must be before end date")

        if self.registration_end > self.competition_start:
            raise InvalidCompetitionDataError(message="Registration end date must be before or equal to start date")


@dataclass(frozen=True, slots=True)
class CompetitionVenue:
    """Competition venue with format and location."""

    format: CompetitionFormat
    location: str | None

    def __post_init__(self) -> None:
        """Validate that location is provided for offline or hybrid formats."""
        if self.format in (CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID) and self.location is None:
            raise InvalidCompetitionDataError(message="Location is required for offline or hybrid format")


class Competition(Entity):
    """Hackathon or olympiad event created by an organizer."""

    id: CompetitionId
    organizer_id: OrganizerId
    title: str
    banner: Banner | None
    description: str
    schedule: CompetitionSchedule
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Validate competition data."""
        if not self.domains:
            raise InvalidCompetitionDataError(message="Domains list must not be empty")
