import structlog
from pydantic import BaseModel

from dreamteams.application.common.application_form_cache import ApplicationFormCache
from dreamteams.application.common.blocked_user_cache import BlockedUserCache
from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import UserId

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
    blocked_cache: BlockedUserCache
    application_form_cache: ApplicationFormCache
    competition_cache: CompetitionCache

    async def execute(self, data: UnblockUserForm) -> None:
        """Unblock the target user and invalidate the blocked-user cache entry."""
        user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(user_id)
        if admin is None:
            raise UserNotFoundError(user_id=user_id)

        target = await self.user_gateway.get(data.target_user_id)
        if target is None:
            raise UserNotFoundError(user_id=data.target_user_id)

        target.unblock(admin)
        await self.uow.commit()
        await self.blocked_cache.delete(data.target_user_id)
        await self.application_form_cache.clear()
        await self.competition_cache.clear_read()
        await self.competition_cache.clear_preview()

        logger.info("User unblocked", target_user_id=data.target_user_id, admin_user_id=user_id)
