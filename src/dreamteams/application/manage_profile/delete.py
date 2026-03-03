import structlog

from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class DeleteProfile:
    """Interactor for deleting user profile."""

    uow: UoW
    idp: IdProvider

    async def execute(self) -> None:
        """Delete user profile."""
        user = await self.idp.get_user()
        logger.debug("Removing user profile", user_id=user.id)

        await self.uow.delete(user)
        await self.uow.commit()
