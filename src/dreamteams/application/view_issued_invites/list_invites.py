from datetime import datetime

import structlog
from pydantic import BaseModel

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import OrganizerId, OrganizerInviteId, UserId
from dreamteams.entities.organizer_invite import ensure_can_list_invites
from dreamteams.entities.user import Organizer

logger: Logger = structlog.get_logger(__name__)
PAGE_SIZE = 20


class OrganizerInfo(BaseModel):
    """Basic organizer info embedded in invite responses."""

    id: OrganizerId
    name: str
    avatar_url: str | None


class InviteModel(BaseModel):
    """Response model representing a single organizer invite."""

    id: OrganizerInviteId
    code: str
    display_name: str | None
    created_by: UserId
    is_revoked: bool
    is_used: bool
    used_by: OrganizerInfo | None
    created_at: datetime


class InvitesList(BaseModel):
    """Paginated list of organizer invites."""

    items: list[InviteModel]
    total: int
    page: int


def _organizer_info(organizer: Organizer, avatar_storage: AvatarStorage) -> OrganizerInfo:
    return OrganizerInfo(
        id=organizer.id,
        name=organizer.organizer_name,
        avatar_url=avatar_storage.get_url(organizer.user.avatar) if organizer.user.avatar else None,
    )


@interactor
class ListInvites:
    """Interactor for listing organizer invites created by the current admin user."""

    idp: IdProvider
    user_gateway: UserGateway
    avatar_storage: AvatarStorage
    organizer_invite_gateway: OrganizerInviteGateway

    async def execute(self, page: int = 1) -> InvitesList:
        """List all invites created by the current admin, paginated."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        ensure_can_list_invites(user)

        logger.debug("Listing invites", user_id=user_id, page=page)
        invites, total = await self.organizer_invite_gateway.list(
            created_by=user_id,
            page=page,
            page_size=PAGE_SIZE,
        )

        items = [
            InviteModel(
                id=invite.id,
                code=invite.code,
                display_name=invite.display_name,
                created_by=invite.created_by,
                is_revoked=invite.is_revoked,
                is_used=invite.is_used,
                used_by=_organizer_info(invite.used_by, self.avatar_storage) if invite.used_by else None,
                created_at=invite.created_at,
            )
            for invite in invites
        ]

        return InvitesList(items=items, total=total, page=page)
