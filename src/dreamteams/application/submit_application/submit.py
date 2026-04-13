from typing import Any

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application import ApplicationAlreadyExistsError
from dreamteams.entities.application.entity import ApplicationData, application_factory
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class SubmitApplicationInput(BaseModel):
    """Request body for submitting an application to a competition."""

    domains: list[Domain]
    form_data: dict[str, Any] | None = None


class CreatedApplication(BaseModel):
    """Response model containing the identifier of a newly created Application."""

    application_id: ApplicationId


@interactor
class SubmitApplication:
    """Interactor for submitting a registration application to a competition."""

    uow: UoW
    idp: IdProvider
    competition_gateway: CompetitionGateway
    application_gateway: ApplicationGateway
    application_form_gateway: ApplicationFormGateway
    clock: Clock

    async def execute(self, competition_id: CompetitionId, data: SubmitApplicationInput) -> CreatedApplication:
        """Submit a new application to a competition."""
        user = await self.idp.get_user()
        logger.debug("Submitting application", competition_id=competition_id, user_id=user.id)

        if user.participant is None:
            logger.warning("User has no participant profile", user_id=user.id)
            raise AccessDeniedError(message="Only participants can submit applications")

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user.id)
            raise CompetitionNotFoundError

        existing = await self.application_gateway.get_by_participant_and_competition(
            user.participant.id,
            competition_id,
        )
        if existing is not None:
            logger.warning(
                "Application already exists",
                competition_id=competition_id,
                participant_id=user.participant.id,
            )
            raise ApplicationAlreadyExistsError

        form = await self.application_form_gateway.get_by_competition_id(competition_id)

        application = application_factory(
            data=ApplicationData(domains=data.domains, form_data=data.form_data),
            user=user,
            competition=competition,
            clock=self.clock,
            form=form,
        )

        self.uow.add(application)
        await self.uow.commit()

        logger.info(
            "Application submitted",
            application_id=application.id,
            competition_id=competition_id,
            participant_id=user.participant.id,
        )
        return CreatedApplication(application_id=application.id)
