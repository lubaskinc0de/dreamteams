from contextlib import suppress
from typing import override
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

from dreamteams.adapters.db.models import user_table
from dreamteams.adapters.db.models.organizer import organizer_table
from dreamteams.adapters.db.models.participant import participant_table
from dreamteams.application.common.gateway.user import UserGateway, UserListFilters, UserRoleFilter
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Participant, User


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

    @override
    async def get_with_roles(self, user_id: UserId) -> User | None:
        """Loads a user with organizer and participant relationships, including blocked users."""
        result = await self._session.execute(
            select(User)
            .where(user_table.c.id == user_id)
            .options(
                selectinload(User.organizer),  # type: ignore[arg-type]
                selectinload(User.participant).selectinload(Participant.skills),  # type: ignore[arg-type]
                selectinload(User.participant).selectinload(Participant.contacts),  # type: ignore[arg-type]
            ),
        )
        return result.scalar_one_or_none()

    @override
    async def list_with_roles(
        self,
        *,
        page: int,
        page_size: int,
        filters: UserListFilters,
    ) -> tuple[list[User], int]:
        """Return admin-facing users with role summaries and total count."""
        joined_tables = user_table.outerjoin(
            organizer_table,
            organizer_table.c.user_id == user_table.c.id,
        ).outerjoin(
            participant_table,
            participant_table.c.user_id == user_table.c.id,
        )
        query_filters = self._build_list_filters(filters)

        count_query = select(func.count()).select_from(joined_tables).where(*query_filters)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = (
            select(User)
            .select_from(joined_tables)
            .where(*query_filters)
            .options(
                selectinload(User.organizer),  # type: ignore[arg-type]
                selectinload(User.participant),  # type: ignore[arg-type]
            )
            .order_by(user_table.c.created_at.desc(), user_table.c.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    def _build_list_filters(self, filters: UserListFilters) -> list[ColumnElement[bool]]:
        query_filters: list[ColumnElement[bool]] = []
        if filters.is_admin is not None:
            query_filters.append(user_table.c.is_admin.is_(filters.is_admin))
        if filters.is_blocked is not None:
            query_filters.append(user_table.c.is_blocked.is_(filters.is_blocked))
        if filters.role == UserRoleFilter.ORGANIZER:
            query_filters.append(organizer_table.c.id.is_not(None))
        elif filters.role == UserRoleFilter.PARTICIPANT:
            query_filters.append(participant_table.c.id.is_not(None))

        search_value = filters.search.strip() if filters.search is not None else None
        if search_value:
            search_pattern = f"%{search_value.lower()}%"
            search_filters: list[ColumnElement[bool]] = [
                func.lower(organizer_table.c.organizer_name).like(search_pattern),
                func.lower(participant_table.c.full_name).like(search_pattern),
            ]

            with suppress(ValueError):
                search_filters.append(user_table.c.id == UUID(search_value))

            query_filters.append(or_(*search_filters))

        return query_filters
