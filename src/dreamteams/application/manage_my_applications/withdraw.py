import structlog
from opentelemetry import trace

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class WithdrawApplication:
    """Interactor for withdrawing (hard-deleting) a pending application."""

    uow: UoW
    idp: IdProvider
    application_gateway: ApplicationGateway
    metrics: MetricsGateway

    async def execute(self, application_id: ApplicationId) -> None:
        """Withdraw a pending application; only the submitting participant may do this."""
        with _tracer.start_as_current_span("interactor.withdraw_application"):
            user = await self.idp.get_user()
            logger.debug("Withdrawing application", application_id=application_id, user_id=user.id)

            application = await self.application_gateway.get(application_id)
            if application is None:
                logger.warning("Application not found", application_id=application_id, user_id=user.id)
                raise ApplicationNotFoundError

            application.can_withdraw(user)

            await self.uow.delete(application)
            await self.uow.commit()

            self.metrics.record_application_withdrawn()
            logger.info("Application withdrawn", application_id=application_id, user_id=user.id)
