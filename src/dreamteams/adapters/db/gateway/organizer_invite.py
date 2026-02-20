from typing import override

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.organizer_invite import organizer_invite_table
from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.entities.common.identifiers import OrganizerInviteId, UserId
from dreamteams.entities.organizer_invite import OrganizerInvite


class SAOrganizerInviteGateway(OrganizerInviteGateway):
    """SQLAlchemy-based implementation of OrganizerInviteGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_id(self, invite_id: OrganizerInviteId) -> OrganizerInvite | None:
        """Retrieve an invite by its UUID primary key."""
        return await self._session.get(OrganizerInvite, invite_id)

    @override
    async def get_by_code(self, code: str) -> OrganizerInvite | None:
        """Retrieve an invite by its unique code string."""
        query = select(OrganizerInvite).where(organizer_invite_table.c.code == code)
        result = await self._session.scalars(query)
        return result.first()

    @override
    async def list(
        self,
        *,
        created_by: UserId,
        page: int,
        page_size: int,
    ) -> tuple[list[OrganizerInvite], int]:
        """List invites created by a specific admin user, ordered by created_at DESC."""
        filter_by = organizer_invite_table.c.created_by == created_by

        count_query = select(func.count()).where(filter_by)
        total = await self._session.scalar(count_query) or 0

        query = (
            select(OrganizerInvite)
            .where(filter_by)
            .order_by(desc(organizer_invite_table.c.created_at))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await self._session.scalars(query)
        return list(result.all()), total
