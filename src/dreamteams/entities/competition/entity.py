from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.milestone import Milestone, MilestoneData, milestone_factory
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData, schedule_factory
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import Organizer, User

type Banner = str


@model
class Competition(Entity):
    """Hackathon or olympiad event created by an organizer."""

    id: CompetitionId
    organizer_id: OrganizerId
    organizer: Organizer
    title: str
    banner: Banner | None
    description: str
    schedule: CompetitionSchedule
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    milestones: list[Milestone]
    auto_accept: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    def can_read(self, user: User) -> bool:
        """Check if user can read this competition."""
        return user.organizer is not None and self.organizer_id == user.organizer.id

    def can_delete(self, user: User) -> bool:
        """Check if user can delete this competition."""
        return user.organizer is not None and self.organizer_id == user.organizer.id

    def update(
        self,
        data: "UpdateCompetitionData",
        user: User,
        clock: Clock,
    ) -> None:
        """Update competition fields."""
        if user.organizer is None or self.organizer_id != user.organizer.id:
            raise AccessDeniedError(message="Only the organizer who created this competition can update it")

        if not data.description or not data.description.strip():
            raise InvalidCompetitionDataError(message="Description must not be empty")

        if not data.domains:
            raise InvalidCompetitionDataError(message="Domains list must not be empty")

        milestones = [] if data.milestones is None else data.milestones

        timestamps = [m.timestamp for m in milestones]
        if len(timestamps) != len(set(timestamps)):
            raise InvalidCompetitionDataError(message="Milestone timestamps must be unique")

        self.title = data.title
        self.description = data.description
        self.schedule = self.schedule.update(data.schedule, clock)
        self.participant_limits = data.participant_limits
        self.domains = data.domains
        self.participant_type = data.participant_type
        self.venue = data.venue
        self.team_size = data.team_size
        self.auto_accept = data.auto_accept
        self.is_archived = data.is_archived
        self.milestones = milestones
        self.updated_at = clock.now()


@dataclass(slots=True)
class CompetitionData:
    """Data for creating Competition."""

    title: str
    description: str
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    auto_accept: bool = False
    milestones: list[MilestoneData] | None = None


@dataclass(slots=True)
class UpdateCompetitionData:
    """Data for updating a Competition."""

    title: str
    description: str
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    auto_accept: bool
    is_archived: bool
    milestones: list[Milestone] | None = None


def competition_factory(
    data: CompetitionData,
    user: User,
    clock: Clock,
) -> Competition:
    """Create a new competition."""
    if user.organizer is None:
        raise AccessDeniedError(message="Only organizers can create competitions")

    if not data.description or not data.description.strip():
        raise InvalidCompetitionDataError(message="Description must not be empty")

    if not data.domains:
        raise InvalidCompetitionDataError(message="Domains list must not be empty")

    milestones = [] if data.milestones is None else data.milestones

    timestamps = [m.timestamp for m in milestones]
    if len(timestamps) != len(set(timestamps)):
        raise InvalidCompetitionDataError(message="Milestone timestamps must be unique")

    now = clock.now()
    return Competition(
        id=uuid4(),
        organizer_id=user.organizer.id,
        organizer=user.organizer,
        title=data.title,
        banner=None,
        description=data.description,
        schedule=schedule_factory(data.schedule, clock),
        participant_limits=data.participant_limits,
        domains=data.domains,
        participant_type=data.participant_type,
        venue=data.venue,
        team_size=data.team_size,
        milestones=[milestone_factory(milestone, clock) for milestone in milestones],
        auto_accept=data.auto_accept,
        is_archived=True,
        created_at=now,
        updated_at=now,
    )
