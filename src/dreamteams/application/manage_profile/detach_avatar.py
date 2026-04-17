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


@interactor
class DetachAvatar:
    """Interactor for detaching avatar from user profile."""

    uow: UoW
    idp: IdProvider
    storage: AvatarStorage
    metrics: MetricsGateway

    async def execute(self) -> None:
        """Detach avatar from user profile."""
        with _tracer.start_as_current_span("interactor.detach_avatar"):
            user = await self.idp.get_user()
            if user.avatar is None:
                return

            logger.debug("Detaching avatar from user profile", user_id=user.id)
            await self.storage.delete_avatar(user.id)
            user.avatar = None
            await self.uow.commit()
            self.metrics.record_avatar_detached()
