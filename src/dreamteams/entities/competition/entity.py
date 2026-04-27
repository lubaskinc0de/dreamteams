from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData, schedule_factory
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.competition.vo.tags import CompetitionTags
from dreamteams.entities.competition.vo.tracks import CompetitionTracks
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import Organizer

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
    tags: CompetitionTags
    tracks: CompetitionTracks
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    milestones: CompetitionMilestones
    auto_accept: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    def is_owned_by(self, organizer: Organizer) -> bool:
        """Returns True when the competition is owned by the given organizer."""
        return self.organizer_id == organizer.id

    def update(
        self,
        data: "UpdateCompetitionData",
        organizer: Organizer,
        clock: Clock,
    ) -> None:
        """Update competition fields."""
        if not self.is_owned_by(organizer):
            raise AccessDeniedError(message="Only the organizer who created this competition can update it")

        new_schedule = self.schedule.update(data.schedule, clock)
        _validate_team_size_schedule_pairing(data.team_size, new_schedule)

        self.title = data.title
        self.description = data.description
        self.schedule = new_schedule
        self.participant_limits = data.participant_limits
        self.tags = data.tags
        self.tracks = data.tracks
        self.participant_type = data.participant_type
        self.venue = data.venue
        self.team_size = data.team_size
        self.auto_accept = data.auto_accept
        self.is_archived = data.is_archived
        self.milestones = data.milestones if data.milestones is not None else CompetitionMilestones()
        self.updated_at = clock.now()


@dataclass(slots=True)
class CompetitionData:
    """Data for creating Competition."""

    title: str
    description: str
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    tags: CompetitionTags
    tracks: CompetitionTracks
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    auto_accept: bool = False
    milestones: list[MilestoneData] | None = None


@dataclass(slots=True)
class UpdateCompetitionData:
    """Data for updating a Competition."""

    title: str
    description: str
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    tags: CompetitionTags
    tracks: CompetitionTracks
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    auto_accept: bool
    is_archived: bool
    milestones: CompetitionMilestones | None = None


def _validate_team_size_schedule_pairing(
    team_size: TeamSizeRange | None,
    schedule: CompetitionSchedule,
) -> None:
    """team_size and schedule.team_formation_* must be set together or both omitted."""
    has_team_formation = schedule.team_formation_start is not None
    has_team_size = team_size is not None
    if has_team_formation != has_team_size:
        raise InvalidCompetitionDataError(
            message="team_size and schedule.team_formation_* must be set together or both omitted",
        )


def competition_factory(
    data: CompetitionData,
    organizer: Organizer,
    clock: Clock,
) -> Competition:
    """Create a new competition."""
    schedule = schedule_factory(data.schedule, clock)
    _validate_team_size_schedule_pairing(data.team_size, schedule)

    now = clock.now()
    return Competition(
        id=uuid4(),
        organizer_id=organizer.id,
        organizer=organizer,
        title=data.title,
        banner=None,
        description=data.description,
        schedule=schedule,
        participant_limits=data.participant_limits,
        tags=data.tags,
        tracks=data.tracks,
        participant_type=data.participant_type,
        venue=data.venue,
        team_size=data.team_size,
        milestones=CompetitionMilestones([milestone_factory(m, clock) for m in (data.milestones or [])]),
        auto_accept=data.auto_accept,
        is_archived=True,
        created_at=now,
        updated_at=now,
    )
