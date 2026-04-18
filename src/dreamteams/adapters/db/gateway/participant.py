from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dreamteams.adapters.db.models import participant_table
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Participant


class SAParticipantGateway(ParticipantGateway):
    """SQLAlchemy-based implementation of ParticipantGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get_by_user_id(self, user_id: UserId) -> Participant | None:
        """Loads the participant attached to a user, with skills and contacts eagerly populated."""
        result = await self._session.execute(
            select(Participant)
            .where(participant_table.c.user_id == user_id)
            .options(
                selectinload(Participant.skills),  # type: ignore[arg-type]
                selectinload(Participant.contacts),  # type: ignore[arg-type]
            ),
        )
        return result.scalar_one_or_none()
