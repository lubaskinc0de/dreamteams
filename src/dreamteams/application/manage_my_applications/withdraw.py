import structlog

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId

logger: Logger = structlog.get_logger(__name__)


@interactor
class WithdrawApplication:
    """Interactor for withdrawing (hard-deleting) a pending application."""

    uow: UoW
    idp: IdProvider
    application_gateway: ApplicationGateway

    async def execute(self, application_id: ApplicationId) -> None:
        """Withdraw a pending application; only the submitting participant may do this."""
        user = await self.idp.get_user()
        logger.debug("Withdrawing application", application_id=application_id, user_id=user.id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user.id)
            raise ApplicationNotFoundError

        application.can_withdraw(user)

        await self.uow.delete(application)
        await self.uow.commit()

        logger.info("Application withdrawn", application_id=application_id, user_id=user.id)
