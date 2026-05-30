from typing import override

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dreamteams.adapters.db.models.organizer_invite import organizer_invite_table
from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.entities.common.identifiers import OrganizerInviteId, UserId
from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import Organizer


class SAOrganizerInviteGateway(OrganizerInviteGateway):
    """SQLAlchemy-based implementation of OrganizerInviteGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_id(self, invite_id: OrganizerInviteId, *, for_update: bool = False) -> OrganizerInvite | None:
        """Retrieve an invite by its UUID primary key."""
        query = (
            select(OrganizerInvite)
            .where(organizer_invite_table.c.id == invite_id)
            .options(selectinload(OrganizerInvite.used_by).selectinload(Organizer.user))  # type: ignore[arg-type]
        )
        if for_update:
            query = query.with_for_update(of=organizer_invite_table)

        result = await self._session.execute(
            query,
        )
        return result.scalar_one_or_none()

    @override
    async def get_by_code(self, code: str, *, for_update: bool = False) -> OrganizerInvite | None:
        """Retrieve an invite by its unique code string."""
        query = select(OrganizerInvite).where(organizer_invite_table.c.code == code)
        if for_update:
            query = query.with_for_update(of=organizer_invite_table)

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
            .options(selectinload(OrganizerInvite.used_by).selectinload(Organizer.user))  # type: ignore[arg-type]
        )

        result = await self._session.scalars(query)
        return list(result.all()), total
