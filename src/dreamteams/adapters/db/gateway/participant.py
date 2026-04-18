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
    async def get_by_user_id(
        self,
        user_id: UserId,
        *,
        eager_skills_and_contacts: bool = False,
    ) -> Participant | None:
        """Load the participant attached to a user; eager-load skills/contacts only when requested."""
        query = select(Participant).where(participant_table.c.user_id == user_id)
        if eager_skills_and_contacts:
            query = query.options(
                selectinload(Participant.skills),  # type: ignore[arg-type]
                selectinload(Participant.contacts),  # type: ignore[arg-type]
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
