# mypy: disable-error-code="empty-body"
from typing import override

from adaptix.conversion import coercer, impl_converter
from opentelemetry import trace
from sqlalchemy import ColumnElement, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dreamteams.adapters.db.models.application import application_table
from dreamteams.adapters.db.models.competition import competition_table
from dreamteams.adapters.db.models.participant import participant_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.application.common.dto.application import ApplicationModel, MyApplicationModel, ParticipantInfo
from dreamteams.application.common.gateway.application import ApplicationGateway, ApplicationSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.user import Participant

_tracer = trace.get_tracer("dreamteams.adapters")

_SORT_COLUMN = {
    ApplicationSortBy.CREATED_AT: application_table.c.created_at,
}


def _order_by(sort_by: ApplicationSortBy, sort_order: SortOrder) -> list[ColumnElement[object]]:
    """Build the ORDER BY clause with a stable id tiebreaker."""
    direction = desc if sort_order == SortOrder.DESC else asc
    return [direction(_SORT_COLUMN[sort_by]), direction(application_table.c.id)]


@impl_converter
def _to_my_application_model(application: Application, competition_name: str) -> MyApplicationModel: ...


@impl_converter(recipe=[coercer(Age, int, func=lambda a: a.value)])
def _to_participant_info(participant: Participant) -> ParticipantInfo: ...


@impl_converter(recipe=[coercer(Participant, ParticipantInfo, func=_to_participant_info)])
def _to_application_model(
    application: Application,
    competition_name: str,
    participant: Participant,
) -> ApplicationModel: ...


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
    async def count_accepted_by_competition(self, competition_id: CompetitionId) -> int:
        """Count applications with ACCEPTED status for a given competition."""
        query = select(func.count()).where(
            application_table.c.competition_id == competition_id,
            application_table.c.status == ApplicationStatus.ACCEPTED,
        )
        return await self._session.scalar(query) or 0

    @override
    async def list_by_participant_with_competition(
        self,
        participant_id: ParticipantId,
        *,
        page: int,
        page_size: int,
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[MyApplicationModel], int]:
        """List applications JOIN-ed with competitions.title, returning MyApplicationModel directly."""
        filters: list[ColumnElement[bool]] = [application_table.c.participant_id == participant_id]
        if status is not None:
            filters.append(application_table.c.status == status)

        with _tracer.start_as_current_span("db.application_list_by_participant_with_competition"):
            total_col = func.count().over().label("total")
            query = (
                select(Application, competition_table.c.title, total_col)
                .join(competition_table, application_table.c.competition_id == competition_table.c.id)
                .where(*filters)
                .order_by(*_order_by(sort_by, sort_order))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            rows = list((await self._session.execute(query)).all())
            total = rows[0].total if rows else 0
            items = [_to_my_application_model(app, title) for app, title, _ in rows]
            return items, total

    @override
    async def list_by_competition_with_participant(
        self,
        competition_id: CompetitionId,
        competition_name: str,
        *,
        page: int,
        page_size: int,
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[ApplicationModel], int]:
        """List applications JOIN-ed with participants (+ eager-loaded skills/contacts) in one query."""
        filters: list[ColumnElement[bool]] = [application_table.c.competition_id == competition_id]
        if status is not None:
            filters.append(application_table.c.status == status)

        with _tracer.start_as_current_span("db.application_list_by_competition_with_participant"):
            total_col = func.count().over().label("total")
            query = (
                select(Application, Participant, total_col)
                .join(Participant, application_table.c.participant_id == participant_table.c.id)
                .join(user_table, user_table.c.id == participant_table.c.user_id)
                .options(
                    selectinload(Participant.skills),  # type: ignore[arg-type]
                    selectinload(Participant.contacts),  # type: ignore[arg-type]
                )
                .where(*filters, user_table.c.is_blocked.is_(False))
                .order_by(*_order_by(sort_by, sort_order))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            rows = list((await self._session.execute(query)).all())
            total = rows[0].total if rows else 0
            items = [_to_application_model(app, competition_name, participant) for app, participant, _ in rows]
            return items, total
