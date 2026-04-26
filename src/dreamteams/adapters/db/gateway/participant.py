from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dreamteams.adapters.db.models import participant_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.entities.common.identifiers import ParticipantId, UserId
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
        """Load the participant attached to a user; returns None if the user is blocked."""
        query = (
            select(Participant)
            .join(user_table, user_table.c.id == participant_table.c.user_id)
            .where(participant_table.c.user_id == user_id, user_table.c.is_blocked.is_(False))
        )
        if eager_skills_and_contacts:
            query = query.options(
                selectinload(Participant.skills),  # type: ignore[arg-type]
                selectinload(Participant.contacts),  # type: ignore[arg-type]
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    @override
    async def get(
        self,
        participant_id: ParticipantId,
        *,
        eager_skills_and_contacts: bool = False,
    ) -> Participant | None:
        """Load the participant by their entity ID; returns None if the user is blocked."""
        query = (
            select(Participant)
            .join(user_table, user_table.c.id == participant_table.c.user_id)
            .where(participant_table.c.id == participant_id, user_table.c.is_blocked.is_(False))
        )
        if eager_skills_and_contacts:
            query = query.options(
                selectinload(Participant.skills),  # type: ignore[arg-type]
                selectinload(Participant.contacts),  # type: ignore[arg-type]
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
