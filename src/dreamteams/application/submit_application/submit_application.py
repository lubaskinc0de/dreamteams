from typing import Any

import structlog
from pydantic import BaseModel

from dreamteams.application.common.application_form_cache import ApplicationFormCache
from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.errors.application import ApplicationAlreadyExistsError
from dreamteams.entities.application.entity import ApplicationData, ApplicationStatus
from dreamteams.entities.application.submit_service import submit_application
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class SubmitApplicationInput(BaseModel):
    """Request body for submitting an application to a competition."""

    track: CompetitionTrackForm
    form_data: dict[str, Any] | None = None


class CreatedApplication(BaseModel):
    """Response model containing the identifier of a newly created Application."""

    application_id: ApplicationId


@interactor
class SubmitApplication:
    """Interactor for submitting a registration application to a competition."""

    uow: UoW
    idp: IdProvider
    participant_gateway: ParticipantGateway
    competition_gateway: CompetitionGateway
    application_gateway: ApplicationGateway
    application_form_gateway: ApplicationFormGateway
    application_form_cache: ApplicationFormCache
    competition_cache: CompetitionCache
    clock: Clock
    metrics: MetricsGateway

    async def execute(self, competition_id: CompetitionId, data: SubmitApplicationInput) -> CreatedApplication:
        """Submit a new application to a competition."""
        user_id = await self.idp.get_user_id()
        logger.debug("Submitting application", competition_id=competition_id, user_id=user_id)

        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None:
            logger.warning("User has no participant profile", user_id=user_id)
            raise AccessDeniedError(message="Only participants can submit applications")

        competition = await self.competition_gateway.get(competition_id, eager_tracks=True)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        existing = await self.application_gateway.get_by_participant_and_competition(
            participant.id,
            competition_id,
        )
        if existing is not None:
            logger.warning(
                "Application already exists",
                competition_id=competition_id,
                participant_id=participant.id,
            )
            raise ApplicationAlreadyExistsError

        accepted_count = await self.application_gateway.count_accepted_by_competition(competition_id)
        form = await self.application_form_cache.get(competition_id)
        if form is None:
            form = await self.application_form_gateway.get_by_competition_id(competition_id)
            if form is not None:
                await self.application_form_cache.set(competition_id, form)

        application = submit_application(
            data=ApplicationData(
                track=CompetitionTrack(data.track.name),
                form_data=data.form_data,
            ),
            participant=participant,
            competition=competition,
            accepted_count=accepted_count,
            clock=self.clock,
            form=form,
        )

        self.uow.add(application)
        await self.uow.commit()

        if application.status == ApplicationStatus.ACCEPTED:
            await self.competition_cache.delete_read(competition_id)
            await self.competition_cache.clear_preview()
        self.metrics.record_application_submitted()

        logger.info(
            "Application submitted",
            application_id=application.id,
            competition_id=competition_id,
            participant_id=participant.id,
        )
        return CreatedApplication(application_id=application.id)
