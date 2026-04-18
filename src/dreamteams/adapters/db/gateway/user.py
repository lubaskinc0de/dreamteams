from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import user_table
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import User


class SAUserGateway(UserGateway):
    """SQLAlchemy-based implementation of UserGateway for reading user entities from PostgreSQL database."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, user_id: UserId) -> User | None:
        """Loads a bare user without organizer/participant relationships."""
        result = await self._session.execute(
            select(User).where(user_table.c.id == user_id),
        )
        return result.scalar_one_or_none()
