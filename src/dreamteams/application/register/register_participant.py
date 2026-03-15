from uuid import uuid4

import structlog
from pydantic import BaseModel, Field, HttpUrl

from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.entities.common.identifiers import ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.entity import (
    ExperienceLevel,
    Participant,
    ParticipantData,
    participant_factory,
)
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill

logger: Logger = structlog.get_logger(__name__)


class CreatedParticipant(BaseModel):
    """Response model containing the info about newly created ``Participant``."""

    participant_id: ParticipantId
    user_id: UserId


class ParticipantForm(BaseModel):
    """Form for registering as ``Participant``."""

    full_name: str = Field(max_length=70)
    avatar_url: HttpUrl | None = None
    bio: str = Field(max_length=500)
    skills: list[ParticipantSkill]
    experience_level: list[ExperienceLevel]
    preferred_domains: list[Domain]
    contacts: list[ParticipantContact]


@interactor
class RegisterParticipant:
    """Interactor for registering as ``Participant``."""

    uow: UoW
    user_factory: UserFactory

    async def execute(self, data: ParticipantForm) -> CreatedParticipant:
        """Creates a new ``User`` and ``Participant`` role."""
        logger.debug("Registering as participant", **data.model_dump())

        user = await self.user_factory.create_user()

        participant_data = ParticipantData(
            full_name=data.full_name,
            avatar_url=data.avatar_url,
            bio=data.bio,
            skills=data.skills,
            experience_level=data.experience_level,
            preferred_domains=data.preferred_domains,
            contacts=data.contacts,
        )

        participant = participant_factory(
            data=participant_data,
            user=user,
            clock=self.uow.cl
        )

