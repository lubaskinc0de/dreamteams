from typing import override

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.application import application_table
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId


class SAApplicationGateway(ApplicationGateway):
    """SQLAlchemy-based implementation of ApplicationGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, application_id: ApplicationId) -> Application | None:
        """Retrieve an application by its unique identifier, returns None if not found."""
        return await self._session.get(Application, application_id)

    @override
    async def get_by_participant_and_competition(
        self,
        participant_id: ParticipantId,
        competition_id: CompetitionId,
    ) -> Application | None:
        """Retrieve an application by participant and competition, returns None if not found."""
        query = select(Application).where(
            application_table.c.participant_id == participant_id,
            application_table.c.competition_id == competition_id,
        )
        result = await self._session.scalars(query)
        return result.first()

    @override
    async def list_by_competition(
        self,
        competition_id: CompetitionId,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Application], int]:
        """List applications for a competition with pagination ordered by created_at DESC."""
        where = application_table.c.competition_id == competition_id
        total = await self._session.scalar(select(func.count()).where(where)) or 0
        query = (
            select(Application)
            .where(where)
            .order_by(desc(application_table.c.created_at))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        result = await self._session.scalars(query)
        return list(result.all()), total

    @override
    async def list_by_participant(
        self,
        participant_id: ParticipantId,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Application], int]:
        """List applications submitted by a participant with pagination ordered by created_at DESC."""
        where = application_table.c.participant_id == participant_id
        total = await self._session.scalar(select(func.count()).where(where)) or 0
        query = (
            select(Application)
            .where(where)
            .order_by(desc(application_table.c.created_at))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        result = await self._session.scalars(query)
        return list(result.all()), total

    @override
    async def count_accepted_by_competition(self, competition_id: CompetitionId) -> int:
        """Count applications with ACCEPTED status for a given competition."""
        query = select(func.count()).where(
            application_table.c.competition_id == competition_id,
            application_table.c.status == ApplicationStatus.ACCEPTED,
        )
        return await self._session.scalar(query) or 0
