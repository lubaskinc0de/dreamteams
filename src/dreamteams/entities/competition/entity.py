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
from dreamteams.entities.user import User

type Banner = str


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
    milestones: list[Milestone]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    def can_read(self, user: User) -> bool:
        """Check if user can read this competition."""
        return user.organizer is not None and self.organizer_id == user.organizer.id

    def can_delete(self, user: User) -> bool:
        """Check if user can delete this competition."""
        return user.organizer is not None and self.organizer_id == user.organizer.id

    def update(  # noqa: PLR0913
        self,
        user: User,
        title: str,
        description: str,
        schedule: ScheduleData,
        participant_limits: ParticipantLimits,
        domains: list[Domain],
        participant_type: ParticipantType,
        venue: CompetitionVenue,
        team_size: TeamSizeRange,
        clock: Clock,
        milestones: list[Milestone] | None = None,
        *,
        is_archived: bool,
    ) -> None:
        """Update competition fields."""
        if user.organizer is None or self.organizer_id != user.organizer.id:
            raise AccessDeniedError(message="Only the organizer who created this competition can update it")

        if not description or not description.strip():
            raise InvalidCompetitionDataError(message="Description must not be empty")

        if not domains:
            raise InvalidCompetitionDataError(message="Domains list must not be empty")

        if milestones is None:
            milestones = []

        timestamps = [m.timestamp for m in milestones]
        if len(timestamps) != len(set(timestamps)):
            raise InvalidCompetitionDataError(message="Milestone timestamps must be unique")

        self.title = title
        self.description = description
        self.schedule = self.schedule.update(schedule, clock)
        self.participant_limits = participant_limits
        self.domains = domains
        self.participant_type = participant_type
        self.venue = venue
        self.team_size = team_size
        self.is_archived = is_archived
        self.milestones = milestones
        self.updated_at = clock.now()


def competition_factory(  # noqa: PLR0913
    *,
    user: User,
    title: str,
    description: str,
    schedule: ScheduleData,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    participant_type: ParticipantType,
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    clock: Clock,
    milestones: list[MilestoneData] | None = None,
) -> Competition:
    """Create a new competition."""
    if user.organizer is None:
        raise AccessDeniedError(message="Only organizers can create competitions")

    if not description or not description.strip():
        raise InvalidCompetitionDataError(message="Description must not be empty")

    if not domains:
        raise InvalidCompetitionDataError(message="Domains list must not be empty")

    if milestones is None:
        milestones = []

    timestamps = [m.timestamp for m in milestones]
    if len(timestamps) != len(set(timestamps)):
        raise InvalidCompetitionDataError(message="Milestone timestamps must be unique")

    now = clock.now()
    return Competition(
        id=uuid4(),
        organizer_id=user.organizer.id,
        title=title,
        banner=None,
        description=description,
        schedule=schedule_factory(schedule, clock),
        participant_limits=participant_limits,
        domains=domains,
        participant_type=participant_type,
        venue=venue,
        team_size=team_size,
        milestones=[milestone_factory(milestone, clock) for milestone in milestones],
        is_archived=True,
        created_at=now,
        updated_at=now,
    )
