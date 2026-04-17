import structlog
from opentelemetry import trace

from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application_form import ApplicationFormNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class DeleteApplicationForm:
    """Interactor for deleting the application form of a competition."""

    uow: UoW
    idp: IdProvider
    competition_gateway: CompetitionGateway
    application_form_gateway: ApplicationFormGateway
    metrics: MetricsGateway

    async def execute(self, competition_id: CompetitionId) -> None:
        """Delete the application form attached to a competition."""
        with _tracer.start_as_current_span("interactor.delete_application_form"):
            user = await self.idp.get_user()
            logger.debug("Deleting application form", competition_id=competition_id, user_id=user.id)

            competition = await self.competition_gateway.get(competition_id)
            if competition is None:
                logger.warning("Competition not found", competition_id=competition_id, user_id=user.id)
                raise CompetitionNotFoundError

            if not competition.can_delete(user):
                logger.warning(
                    "Access denied to delete application form",
                    competition_id=competition_id,
                    user_id=user.id,
                )
                raise AccessDeniedError(message="Only the organizer who created this competition can delete its form")

            form = await self.application_form_gateway.get_by_competition_id(competition_id)
            if form is None:
                logger.warning("Application form not found", competition_id=competition_id, user_id=user.id)
                raise ApplicationFormNotFoundError

            await self.uow.delete(form)
            await self.uow.commit()

            self.metrics.record_application_form_deleted()
            logger.info("Application form deleted", competition_id=competition_id, user_id=user.id)
