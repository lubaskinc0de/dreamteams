import structlog
from pydantic import BaseModel

from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import UserBlocked
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import UserId
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class BlockUserForm(BaseModel):
    """Form for blocking a user account."""

    target_user_id: UserId
    reason: str | None = None


@interactor
class BlockUser:
    """Interactor for blocking a user account. Admin only."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    event_bus: EventBus
    clock: Clock

    async def execute(self, data: BlockUserForm) -> None:
        """Block the target user."""
        user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(user_id)
        if admin is None:
            raise UserNotFoundError(user_id=user_id)

        target = await self.user_gateway.get(data.target_user_id)
        if target is None:
            raise UserNotFoundError(user_id=data.target_user_id)

        target.block(admin, data.reason, self.clock)
        await self.uow.commit()
        await self.event_bus.publish(UserBlocked(user_id=data.target_user_id, ban_status=target.ban_status))

        logger.info("User blocked", target_user_id=data.target_user_id, admin_user_id=user_id)
