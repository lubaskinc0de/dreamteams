import structlog

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class DetachAvatar:
    """Interactor for detaching avatar from user profile."""

    uow: UoW
    idp: IdProvider
    storage: AvatarStorage

    async def execute(self) -> None:
        """Detach avatar from user profile."""
        user = await self.idp.get_user()
        if user.avatar is None:
            return

        logger.debug("Detaching avatar from user profile", user_id=user.id)
        await self.storage.delete_avatar(user.id)
        user.avatar = None
        await self.uow.commit()
