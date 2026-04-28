from dataclasses import dataclass
from typing import BinaryIO

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


@dataclass(slots=True, frozen=True)
class AvatarForm:
    """Form for attaching avatar to user profile."""

    file_data: BinaryIO
    content_type: str


@interactor
class AttachAvatar:
    """Interactor for attaching avatar to user profile."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    storage: AvatarStorage
    metrics: MetricsGateway

    async def execute(self, data: AvatarForm) -> None:
        """Attach avatar to user profile."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        logger.debug("Attaching avatar to user profile", user_id=user_id)

        if user.avatar is not None:
            await self.storage.delete_avatar(user_id)
        avatar_key = await self.storage.upload_avatar(user_id, data.file_data, data.content_type)
        user.avatar = avatar_key
        await self.uow.commit()
        self.metrics.record_avatar_attached()
