import structlog

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class DetachAvatar:
    """Interactor for detaching avatar from user profile."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    storage: AvatarStorage
    metrics: MetricsGateway

    async def execute(self) -> None:
        """Detach avatar from user profile."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        if user.avatar is None:
            return

        logger.debug("Detaching avatar from user profile", user_id=user_id)
        await self.storage.delete_avatar(user_id)
        user.avatar = None

        await self.uow.commit()
        self.metrics.record_avatar_detached()
