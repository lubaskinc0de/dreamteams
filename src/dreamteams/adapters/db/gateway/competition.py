from typing import override

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import milestone_table
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.milestone import Milestone


class SACompetitionGateway(CompetitionGateway):
    """SQLAlchemy-based implementation of CompetitionGateway for reading competition entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, competition_id: CompetitionId) -> Competition | None:
        """Queries the database for a competition by ID using SQLAlchemy session, returns None if not found."""
        return await self._session.get(Competition, competition_id)

    @override
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delete all competition milestones from storage."""
        q = delete(Milestone).where(milestone_table.c.competition_id == competition_id)
        await self._session.execute(q)
