import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.competition_tag import CompetitionTagNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId, CompetitionTagId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.competition.entity import UpdateCompetitionGeneralInfoData
from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.competition.milestones import CompetitionMilestones
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.tags import CompetitionTags
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.tracks import CompetitionTracks
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class UpdateCompetitionGeneralInfoForm(BaseModel):
    """Form for updating competition general information."""

    title: str = Field(max_length=200)
    description: str = Field(min_length=1)
    participant_limits: ParticipantLimits
    tag_ids: list[CompetitionTagId] = Field(default_factory=list, max_length=30)
    tracks: list[CompetitionTrackForm] = Field(min_length=1)
    participant_type: ParticipantType
    venue: CompetitionVenue
    milestones: list[MilestoneForm] | None
    auto_accept: bool


@interactor
class UpdateCompetitionGeneralInfo:
    """Interactor for updating competition general information."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    competition_tag_gateway: CompetitionTagGateway
    competition_cache: CompetitionCache
    clock: Clock

    async def execute(self, competition_id: CompetitionId, data: UpdateCompetitionGeneralInfoForm) -> None:
        """Update competition general information by organizer who created it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Updating competition general information", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(
            competition_id,
            eager_milestones=True,
            eager_tags=True,
            eager_tracks=True,
        )
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        if data.milestones is not None:
            await self.competition_gateway.clear_milestones(competition_id)
        await self.competition_gateway.clear_tracks(competition_id)

        loaded_tags = await self.competition_tag_gateway.get_many(data.tag_ids)
        tag_by_id = {tag.id: tag for tag in loaded_tags}
        if set(data.tag_ids) != set(tag_by_id):
            raise CompetitionTagNotFoundError

        tags = [tag_by_id[tag_id] for tag_id in data.tag_ids]
        competition.update_general_info(
            organizer=organizer,
            clock=self.clock,
            data=UpdateCompetitionGeneralInfoData(
                title=data.title,
                description=data.description,
                participant_limits=data.participant_limits,
                tags=CompetitionTags(tags),
                tracks=CompetitionTracks([CompetitionTrack(track.name) for track in data.tracks]),
                participant_type=data.participant_type,
                venue=data.venue,
                milestones=CompetitionMilestones(
                    [
                        milestone_factory(
                            MilestoneData(
                                title=milestone.title,
                                timestamp=milestone.timestamp,
                                description=milestone.description,
                            ),
                            self.clock,
                        )
                        for milestone in data.milestones
                    ],
                )
                if data.milestones is not None
                else None,
                auto_accept=data.auto_accept,
            ),
        )

        await self.uow.commit()
        await self.competition_cache.delete_read(competition_id)
        await self.competition_cache.clear_preview()

        logger.info("Competition general information updated", competition_id=competition_id, user_id=user_id)
