from datetime import datetime

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.entities.common.identifiers import OrganizerInviteId, UserId
from dreamteams.entities.organizer_invite import ensure_can_list_invites

logger: Logger = structlog.get_logger(__name__)

PAGE_SIZE = 20


class InviteModel(BaseModel):
    """Response model representing a single organizer invite."""

    id: OrganizerInviteId
    code: str
    display_name: str | None
    created_by: UserId
    is_revoked: bool
    is_used: bool
    created_at: datetime


class InvitesList(BaseModel):
    """Paginated list of organizer invites."""

    items: list[InviteModel]
    total: int
    page: int


@interactor
class ListInvites:
    """Interactor for listing organizer invites created by the current admin user."""

    idp: IdProvider
    organizer_invite_gateway: OrganizerInviteGateway

    async def execute(self, page: int = 1) -> InvitesList:
        """List all invites created by the current admin, paginated."""
        user = await self.idp.get_user()
        ensure_can_list_invites(user)

        logger.debug("Listing invites", user_id=user.id, page=page)
        invites, total = await self.organizer_invite_gateway.list(
            created_by=user.id,
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
                created_at=invite.created_at,
            )
            for invite in invites
        ]

        return InvitesList(items=items, total=total, page=page)
