from typing import override

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.organizer import organizer_table
from dreamteams.application.common.gateway.organizer import OrganizerGateway


class SAOrganizerGateway(OrganizerGateway):
    """SQLAlchemy database gateway for organizer operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def is_unique(self, phone_number: str, contact_email: str) -> bool:
        """Check if organizer with given phone number or contact email already exists.

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
