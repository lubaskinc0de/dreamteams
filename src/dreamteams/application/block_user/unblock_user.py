import structlog
from pydantic import BaseModel

from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import UserUnblocked
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import UserId
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class UnblockUserForm(BaseModel):
    """Form for unblocking a user account."""

    target_user_id: UserId


@interactor
class UnblockUser:
    """Interactor for unblocking a user account. Admin only."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    event_bus: EventBus

    async def execute(self, data: UnblockUserForm) -> None:
        """Unblock the target user."""
        user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(user_id)
        if admin is None:
            raise UserNotFoundError(user_id=user_id)

        target = await self.user_gateway.get(data.target_user_id)
        if target is None:
            raise UserNotFoundError(user_id=data.target_user_id)

        target.unblock(admin)
        await self.uow.commit()
        await self.event_bus.publish(UserUnblocked(user_id=data.target_user_id))

        logger.info("User unblocked", target_user_id=data.target_user_id, admin_user_id=user_id)
