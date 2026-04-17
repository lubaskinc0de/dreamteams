import structlog
from opentelemetry import trace

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class RejectApplication:
    """Interactor for rejecting a pending application (PENDING → REJECTED)."""

    uow: UoW
    idp: IdProvider
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway
    metrics: MetricsGateway

    async def execute(self, application_id: ApplicationId) -> None:
        """Reject a pending application; delegates access and status checks to the domain."""
        with _tracer.start_as_current_span("interactor.reject_application"):
            user = await self.idp.get_user()
            logger.debug("Rejecting application", application_id=application_id, user_id=user.id)

            application = await self.application_gateway.get(application_id)
            if application is None:
                logger.warning("Application not found", application_id=application_id, user_id=user.id)
                raise ApplicationNotFoundError

            competition = await self.competition_gateway.get(application.competition_id)
            if competition is None:
                raise CompetitionNotFoundError

            application.reject(user, competition)

            self.uow.add(application)
            await self.uow.commit()

            self.metrics.record_application_rejected()
            logger.info("Application rejected", application_id=application_id, user_id=user.id)
