from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.application_form import application_form_table
from dreamteams.adapters.db.models.competition import competition_table
from dreamteams.adapters.db.models.organizer import organizer_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.identifiers import CompetitionId


class SAApplicationFormGateway(ApplicationFormGateway):
    """SQLAlchemy-based implementation of ApplicationFormGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """
        Retrieve the application form for a given competition.

        Returns None if not found or if the competition's organizer account is blocked.
        """
        query = (
            select(ApplicationForm)
            .join(competition_table, competition_table.c.id == application_form_table.c.competition_id)
            .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
            .join(user_table, user_table.c.id == organizer_table.c.user_id)
            .where(
                application_form_table.c.competition_id == competition_id,
                user_table.c.is_blocked.is_(False),
            )
        )
        result = await self._session.scalars(query)
        return result.first()
