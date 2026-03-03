from dataclasses import dataclass
from typing import BinaryIO

import structlog

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW

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
    storage: AvatarStorage

    async def execute(self, data: AvatarForm) -> None:
        """Attach avatar to user profile."""
        user = await self.idp.get_user()
        logger.debug("Attaching avatar to user profile", user_id=user.id)

        if user.avatar is not None:
            await self.storage.delete_avatar(user.id)
        avatar_key = await self.storage.upload_avatar(user.id, data.file_data, data.content_type)
        user.avatar = avatar_key
        await self.uow.commit()
