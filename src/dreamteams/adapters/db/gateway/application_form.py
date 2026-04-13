from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.application_form import application_form_table
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.identifiers import CompetitionId


class SAApplicationFormGateway(ApplicationFormGateway):
    """SQLAlchemy-based implementation of ApplicationFormGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Retrieve the application form for a given competition, returns None if not found."""
        query = select(ApplicationForm).where(application_form_table.c.competition_id == competition_id)
        result = await self._session.scalars(query)
        return result.first()
