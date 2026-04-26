import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.user import UserGateway, UserListFilters, UserRoleFilter
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.manage_users.shared import ensure_admin
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus

logger: Logger = structlog.get_logger(__name__)
PAGE_SIZE = 20


class ListUsersInput(BaseModel):
    """Input parameters for admin-facing user listing."""

    page: int = Field(ge=1, default=1)
    search: str | None = None
    is_admin: bool | None = None
    is_blocked: bool | None = None
    role: UserRoleFilter | None = None


class AdminUserListItem(BaseModel):
    """Admin-facing list item for user scanning."""

    id: UserId
    is_admin: bool
    ban_status: BanStatus
    organizer_name: str | None
    participant_full_name: str | None


class UsersList(BaseModel):
    """Paginated admin-facing users list."""

    items: list[AdminUserListItem]
    total: int
    page: int


@interactor
class ListUsers:
    """Interactor for listing users as an admin."""

    idp: IdProvider
    user_gateway: UserGateway

    async def execute(self, input_data: ListUsersInput) -> UsersList:
        """List users matching admin filters."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        logger.debug(
            "Listing users by admin",
            admin_user_id=admin_user_id,
            page=input_data.page,
            page_size=PAGE_SIZE,
            search=input_data.search,
            is_admin=input_data.is_admin,
            is_blocked=input_data.is_blocked,
            role=input_data.role,
        )

        users, total = await self.user_gateway.list_with_roles(
            page=input_data.page,
            page_size=PAGE_SIZE,
            filters=UserListFilters(
                search=input_data.search,
                is_admin=input_data.is_admin,
                is_blocked=input_data.is_blocked,
                role=input_data.role,
            ),
        )

        return UsersList(
            items=[
                AdminUserListItem(
                    id=user.id,
                    is_admin=user.is_admin,
                    ban_status=user.ban_status,
                    organizer_name=user.organizer.organizer_name if user.organizer is not None else None,
                    participant_full_name=user.participant.full_name if user.participant is not None else None,
                )
                for user in users
            ],
            total=total,
            page=input_data.page,
        )
