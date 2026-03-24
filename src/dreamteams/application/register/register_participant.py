import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import (
    ExperienceLevel,
    ParticipantData,
    participant_factory,
)

logger: Logger = structlog.get_logger(__name__)


class CreatedParticipant(BaseModel):
    """Response model containing the info about newly created ``Participant``."""

    participant_id: ParticipantId
    user_id: UserId


class ParticipantForm(BaseModel):
    """Form for registering as ``Participant``."""

    full_name: str = Field(min_length=1, max_length=70)
    bio: str = Field(max_length=500)
    skills: list[ParticipantSkillForm]
    experience_level: ExperienceLevel
    preferred_domains: list[Domain]
    contacts: list[ParticipantContactForm]


@interactor
class RegisterParticipant:
    """Interactor for registering as ``Participant``."""

    uow: UoW
    user_factory: UserFactory
    clock: Clock

    async def execute(self, data: ParticipantForm) -> CreatedParticipant:
        """Creates a new ``User`` and ``Participant`` role."""
        logger.debug("Registering as participant", **data.model_dump())

        user = await self.user_factory.create_user()

        participant_data = ParticipantData(
            full_name=data.full_name,
            avatar_url=None,
            bio=data.bio,
            skills=[
                ParticipantSkill(
                    name=s.name,
                    level=s.level,
                )
                for s in data.skills
            ],
            experience_level=data.experience_level,
            preferred_domains=data.preferred_domains,
            contacts=[
                ParticipantContact(
                    title=c.title,
                    url=str(c.url),
                )
                for c in data.contacts
            ],
        )

        participant = participant_factory(
            data=participant_data,
            user=user,
            clock=self.clock,
        )

        logger.debug(
            "Creating role 'Participant' for user",
            user_id=user.id,
            participant_id=participant.id,
        )
        user.make_participant(participant=participant)

        self.uow.add(participant)
        await self.uow.commit()

        logger.info(
            "Participant created",
            user_id=user.id,
            participant_id=participant.id,
        )

        return CreatedParticipant(
            participant_id=participant.id,
            user_id=user.id,
        )
