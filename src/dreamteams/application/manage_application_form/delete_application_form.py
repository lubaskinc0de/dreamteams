import structlog

from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application_form import ApplicationFormNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class DeleteApplicationForm:
    """Interactor for deleting the application form of a competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    application_form_gateway: ApplicationFormGateway
    metrics: MetricsGateway

    async def execute(self, competition_id: CompetitionId) -> None:
        """Delete the application form attached to a competition."""
        user_id = await self.idp.get_user_id()
        logger.debug("Deleting application form", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        if not competition.is_owned_by(organizer):
            logger.warning(
                "Access denied to delete application form",
                competition_id=competition_id,
                user_id=user_id,
            )
            raise AccessDeniedError(message="Only the organizer who created this competition can delete its form")

        form = await self.application_form_gateway.get_by_competition_id(competition_id)
        if form is None:
            logger.warning("Application form not found", competition_id=competition_id, user_id=user_id)
            raise ApplicationFormNotFoundError

        await self.uow.delete(form)
        await self.uow.commit()

        self.metrics.record_application_form_deleted()
        logger.info("Application form deleted", competition_id=competition_id, user_id=user_id)
