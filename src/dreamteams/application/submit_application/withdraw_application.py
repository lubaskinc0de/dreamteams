import structlog

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.application.errors.participant import ParticipantNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class WithdrawApplication:
    """Interactor for withdrawing (hard-deleting) a pending application."""

    uow: UoW
    idp: IdProvider
    participant_gateway: ParticipantGateway
    application_gateway: ApplicationGateway
    metrics: MetricsGateway

    async def execute(self, application_id: ApplicationId) -> None:
        """Withdraw a pending application; only the submitting participant may do this."""
        user_id = await self.idp.get_user_id()
        logger.debug("Withdrawing application", application_id=application_id, user_id=user_id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user_id)
            raise ApplicationNotFoundError

        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None:
            raise ParticipantNotFoundError

        application.ensure_can_withdraw(participant)

        await self.uow.delete(application)
        await self.uow.commit()

        self.metrics.record_application_withdrawn()
        logger.info("Application withdrawn", application_id=application_id, user_id=user_id)
