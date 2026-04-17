from dataclasses import dataclass
from typing import BinaryIO

import structlog
from opentelemetry import trace

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


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
    metrics: MetricsGateway

    async def execute(self, data: AvatarForm) -> None:
        """Attach avatar to user profile."""
        with _tracer.start_as_current_span("interactor.attach_avatar"):
            user = await self.idp.get_user()
            logger.debug("Attaching avatar to user profile", user_id=user.id)

            if user.avatar is not None:
                await self.storage.delete_avatar(user.id)
            avatar_key = await self.storage.upload_avatar(user.id, data.file_data, data.content_type)
            user.avatar = avatar_key
            await self.uow.commit()
            self.metrics.record_avatar_attached()
