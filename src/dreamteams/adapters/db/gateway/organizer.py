from typing import override

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.organizer import organizer_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Organizer


class SAOrganizerGateway(OrganizerGateway):
    """SQLAlchemy database gateway for organizer operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_user_id(self, user_id: UserId) -> Organizer | None:
        """Return the organizer attached to the given user, or None if the user is blocked or has no organizer role."""
        result = await self._session.execute(
            select(Organizer)
            .join(user_table, user_table.c.id == organizer_table.c.user_id)
            .where(organizer_table.c.user_id == user_id, user_table.c.is_blocked.is_(False)),
        )
        return result.scalar_one_or_none()

    @override
    async def is_unique(self, phone_number: str, contact_email: str) -> bool:
        """
        Check if organizer with given phone number or contact email already exists.

        Returns True if no organizer exists with these credentials.
        Returns False if organizer with phone_number or contact_email already exists.
        """
        query = select(organizer_table).where(
            or_(
                organizer_table.c.phone_number == phone_number,
                organizer_table.c.contact_email == contact_email,
            ),
        )
        result = await self._session.execute(query)
        return result.first() is None

    @override
    async def is_unique_by_email(self, contact_email: str) -> bool:
        """
        Check if no organizer with the given contact email exists.

        Returns True if no organizer uses this email.
        """
        query = select(organizer_table).where(
            organizer_table.c.contact_email == contact_email,
        )
        result = await self._session.execute(query)
        return result.first() is None
