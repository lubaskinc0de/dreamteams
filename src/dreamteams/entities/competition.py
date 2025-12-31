from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum, auto
from uuid import uuid4

from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import User

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

        if self.min <= 0:
            raise InvalidCompetitionDataError(message="Min participants must be greater than 0")

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


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime by removing seconds and microseconds."""
    return dt.replace(second=0, microsecond=0)


@dataclass(slots=True)
class CompetitionSchedule:
    """Competition schedule with dates and registration period."""

    competition_start: datetime
    registration_start: datetime
    registration_end: datetime
    competition_end: datetime
    team_formation_start: datetime | None = None
    team_formation_end: datetime | None = None

    def __post_init__(self) -> None:
        """Validate schedule dates and normalize datetime values."""
        if (self.team_formation_start is None) != (self.team_formation_end is None):
            raise InvalidCompetitionDataError(
                message="Both team formation start and end must be specified together or not at all",
            )

        now = normalize_datetime(datetime.now(tz=UTC))

        self._normalize_all_dates()
        self._validate_dates_not_in_past(now)
        self._validate_date_ranges()

    def _normalize_all_dates(self) -> None:
        """Normalize all datetime values."""
        self.registration_start = normalize_datetime(self.registration_start)
        self.registration_end = normalize_datetime(self.registration_end)
        self.competition_start = normalize_datetime(self.competition_start)
        self.competition_end = normalize_datetime(self.competition_end)

        if self.team_formation_start is not None:
            self.team_formation_start = normalize_datetime(self.team_formation_start)
        if self.team_formation_end is not None:
            self.team_formation_end = normalize_datetime(self.team_formation_end)

    def _validate_dates_not_in_past(self, now: datetime) -> None:
        """Validate that all dates are not in the past."""
        if self.registration_start < now:
            raise InvalidCompetitionDataError(message="Registration start date must not be in the past")
        if self.registration_end < now:
            raise InvalidCompetitionDataError(message="Registration end date must not be in the past")
        if self.competition_start < now:
            raise InvalidCompetitionDataError(message="Competition start date must not be in the past")
        if self.competition_end < now:
            raise InvalidCompetitionDataError(message="Competition end date must not be in the past")

        if self.team_formation_start is not None and self.team_formation_end is not None:
            if self.team_formation_start < now:
                raise InvalidCompetitionDataError(message="Team formation start date must not be in the past")
            if self.team_formation_end < now:
                raise InvalidCompetitionDataError(message="Team formation end date must not be in the past")

    def _validate_date_ranges(self) -> None:
        """Validate date ranges are correct."""
        if self.competition_end <= self.competition_start:
            raise InvalidCompetitionDataError(message="End date must be after start date")

        if self.registration_start >= self.registration_end:
            raise InvalidCompetitionDataError(message="Registration start date must be before end date")

        if self.registration_end > self.competition_start:
            raise InvalidCompetitionDataError(message="Registration end date must be before or equal to start date")

        if self.team_formation_start is not None and self.team_formation_end is not None:
            if self.team_formation_start < self.registration_end:
                raise InvalidCompetitionDataError(
                    message="Team formation start must be after or equal to registration end",
                )

            if self.team_formation_end <= self.team_formation_start:
                raise InvalidCompetitionDataError(message="Team formation end must be after start")

            if self.team_formation_end > self.competition_end:
                raise InvalidCompetitionDataError(
                    message="Team formation end must be before or equal to competition end",
                )


@dataclass(frozen=True, slots=True)
class CompetitionVenue:
    """Competition venue with format and location."""

    format: CompetitionFormat
    location: str | None

    def __post_init__(self) -> None:
        """Validate that location is provided for offline or hybrid formats."""
        if self.format in (CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID) and (
            self.location is None or not self.location.strip()
        ):
            raise InvalidCompetitionDataError(message="Location is required for offline or hybrid format")


@model
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
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    def can_delete(self, user: User) -> bool:
        """Check if user can delete this competition."""
        return user.organizer is not None and self.organizer_id == user.organizer.id

    def update(  # noqa: PLR0913
        self,
        user: User,
        title: str,
        description: str,
        schedule: CompetitionSchedule,
        participant_limits: ParticipantLimits,
        domains: list[Domain],
        participant_type: ParticipantType,
        venue: CompetitionVenue,
        team_size: TeamSizeRange,
        *,
        is_archived: bool,
    ) -> None:
        """Update competition fields."""
        if user.organizer is None or self.organizer_id != user.organizer.id:
            raise AccessDeniedError

        if not description or not description.strip():
            raise InvalidCompetitionDataError(message="Description must not be empty")

        if not domains:
            raise InvalidCompetitionDataError(message="Domains list must not be empty")

        self.title = title
        self.description = description
        self.schedule = schedule
        self.participant_limits = participant_limits
        self.domains = domains
        self.participant_type = participant_type
        self.venue = venue
        self.team_size = team_size
        self.is_archived = is_archived
        self.updated_at = datetime.now(tz=UTC)


def competition_factory(  # noqa: PLR0913
    *,
    organizer_id: OrganizerId,
    title: str,
    description: str,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    participant_type: ParticipantType,
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> Competition:
    """Create a new competition."""
    if not description or not description.strip():
        raise InvalidCompetitionDataError(message="Description must not be empty")

    if not domains:
        raise InvalidCompetitionDataError(message="Domains list must not be empty")

    now = datetime.now(tz=UTC)
    return Competition(
        id=uuid4(),
        organizer_id=organizer_id,
        title=title,
        banner=None,
        description=description,
        schedule=schedule,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=participant_type,
        venue=venue,
        team_size=team_size,
        is_archived=True,
        created_at=now,
        updated_at=now,
    )
