import structlog

from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.user import UserNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class DeleteProfile:
    """Interactor for deleting user profile."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway

    async def execute(self) -> None:
        """Delete user profile."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        logger.debug("Removing user profile", user_id=user_id)

        await self.uow.delete(user)
        await self.uow.commit()
