import structlog
from pydantic import BaseModel, Field, model_validator

from dreamteams.application.common.competition_input_limits import (
    MAX_COMPETITION_DESCRIPTION_LENGTH,
    MAX_COMPETITION_MILESTONES,
    MAX_COMPETITION_TRACKS,
    MAX_LOCATION_LENGTH,
    MAX_PARTICIPANTS,
    MAX_TEAM_SIZE,
)
from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import CompetitionCreated
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.competition_tag import CompetitionTagNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId, CompetitionTagId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.competition.entity import CompetitionData, competition_factory
from dreamteams.entities.competition.milestone import MilestoneData
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.tags import CompetitionTags
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.tracks import CompetitionTracks
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


def _validate_competition_bounds(
    participant_limits: ParticipantLimits,
    team_size: TeamSizeRange | None,
    venue: CompetitionVenue,
) -> None:
    """Validate application-level request bounds for competition input."""
    if participant_limits.max > MAX_PARTICIPANTS:
        msg = f"Max participants must be at most {MAX_PARTICIPANTS}"
        raise ValueError(msg)

    if team_size is not None:
        if team_size.max > MAX_TEAM_SIZE:
            msg = f"Max team size must be at most {MAX_TEAM_SIZE}"
            raise ValueError(msg)
        if team_size.min > MAX_TEAM_SIZE:
            msg = f"Min team size must be at most {MAX_TEAM_SIZE}"
            raise ValueError(msg)

    if venue.location is not None and len(venue.location) > MAX_LOCATION_LENGTH:
        msg = f"Location must be at most {MAX_LOCATION_LENGTH} characters"
        raise ValueError(msg)


class CreatedCompetition(BaseModel):
    """Response model containing the created competition identifier."""

    competition_id: CompetitionId


class CompetitionForm(BaseModel):
    """Form for creating a competition."""

    title: str = Field(max_length=200)
    description: str = Field(min_length=1, max_length=MAX_COMPETITION_DESCRIPTION_LENGTH)
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    tag_ids: list[CompetitionTagId] = Field(default_factory=list, max_length=30)
    tracks: list[CompetitionTrackForm] = Field(min_length=1, max_length=MAX_COMPETITION_TRACKS)
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    auto_accept: bool = False
    milestones: list[MilestoneForm] = Field(default_factory=list, max_length=MAX_COMPETITION_MILESTONES)

    @model_validator(mode="after")
    def validate_input_bounds(self) -> "CompetitionForm":
        """Validate application-level request bounds."""
        _validate_competition_bounds(
            participant_limits=self.participant_limits,
            team_size=self.team_size,
            venue=self.venue,
        )
        return self


@interactor
class PublishCompetition:
    """Interactor for creating a new competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_tag_gateway: CompetitionTagGateway
    event_bus: EventBus
    clock: Clock

    async def execute(self, data: CompetitionForm) -> CreatedCompetition:
        """Creates a new competition."""
        user_id = await self.idp.get_user_id()
        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        logger.debug("Creating competition", title=data.title, user_id=user_id)

        loaded_tags = await self.competition_tag_gateway.get_many(data.tag_ids)
        tag_by_id = {tag.id: tag for tag in loaded_tags}
        if set(data.tag_ids) != set(tag_by_id):
            raise CompetitionTagNotFoundError
        tags = [tag_by_id[tag_id] for tag_id in data.tag_ids]

        competition = competition_factory(
            CompetitionData(
                title=data.title,
                description=data.description,
                schedule=data.schedule,
                participant_limits=data.participant_limits,
                tags=CompetitionTags(tags),
                tracks=CompetitionTracks([CompetitionTrack(track.name) for track in data.tracks]),
                participant_type=data.participant_type,
                venue=data.venue,
                team_size=data.team_size,
                auto_accept=data.auto_accept,
                milestones=[
                    MilestoneData(
                        title=milestone.title,
                        timestamp=milestone.timestamp,
                        description=milestone.description,
                    )
                    for milestone in data.milestones
                ],
            ),
            organizer,
            self.clock,
        )

        logger.debug(
            "Competition created",
            competition_id=competition.id,
            user_id=user_id,
        )

        self.uow.add(competition)
        await self.uow.commit()
        await self.event_bus.publish(CompetitionCreated(competition_id=competition.id))

        logger.info("Competition saved", competition_id=competition.id, user_id=user_id)
        return CreatedCompetition(competition_id=competition.id)
