from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.competition import Competition


class SACompetitionGateway(CompetitionGateway):
    """SQLAlchemy-based implementation of CompetitionGateway for reading competition entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, competition_id: CompetitionId) -> Competition | None:
        """Queries the database for a competition by ID using SQLAlchemy session, returns None if not found."""
        return await self._session.get(Competition, competition_id)
