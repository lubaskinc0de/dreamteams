from typing import override

from opentelemetry import trace
from sqlalchemy import ColumnElement, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.application import application_table
from dreamteams.application.common.gateway.application import ApplicationGateway, ApplicationSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId

_tracer = trace.get_tracer("dreamteams.adapters")

_SORT_COLUMN = {
    ApplicationSortBy.CREATED_AT: application_table.c.created_at,
}


def _order_by(sort_by: ApplicationSortBy, sort_order: SortOrder) -> list[ColumnElement[object]]:
    """Build the ORDER BY clause with a stable id tiebreaker."""
    direction = desc if sort_order == SortOrder.DESC else asc
    return [direction(_SORT_COLUMN[sort_by]), direction(application_table.c.id)]


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
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[Application], int]:
        """List applications for a competition with pagination, sorting, and optional status filter."""
        filters: list[ColumnElement[bool]] = [application_table.c.competition_id == competition_id]
        if status is not None:
            filters.append(application_table.c.status == status)

        with _tracer.start_as_current_span("db.application_list_by_competition"):
            total_col = func.count().over().label("total")
            query = (
                select(Application, total_col)
                .where(*filters)
                .order_by(*_order_by(sort_by, sort_order))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            result = list((await self._session.execute(query)).all())
            apps = [row[0] for row in result]
            total = result[0].total if result else 0
            return apps, total

    @override
    async def list_by_participant(
        self,
        participant_id: ParticipantId,
        *,
        page: int,
        page_size: int,
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[Application], int]:
        """List applications submitted by a participant with pagination, sorting, and optional status filter."""
        filters: list[ColumnElement[bool]] = [application_table.c.participant_id == participant_id]
        if status is not None:
            filters.append(application_table.c.status == status)

        with _tracer.start_as_current_span("db.application_list_by_participant"):
            total_col = func.count().over().label("total")
            query = (
                select(Application, total_col)
                .where(*filters)
                .order_by(*_order_by(sort_by, sort_order))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            result = list((await self._session.execute(query)).all())
            apps = [row[0] for row in result]
            total = result[0].total if result else 0
            return apps, total

    @override
    async def count_accepted_by_competition(self, competition_id: CompetitionId) -> int:
        """Count applications with ACCEPTED status for a given competition."""
        query = select(func.count()).where(
            application_table.c.competition_id == competition_id,
            application_table.c.status == ApplicationStatus.ACCEPTED,
        )
        return await self._session.scalar(query) or 0
