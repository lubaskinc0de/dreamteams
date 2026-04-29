import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.participant import ParticipantNotFoundError
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.participant.age import Age
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.participant_skill import ParticipantSkill
from dreamteams.entities.participant.participant_skills import ParticipantSkills
from dreamteams.entities.user import ExperienceLevel, UpdateParticipantData
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class UpdateParticipantForm(BaseModel):
    """Form for updating ``Participant`` profile."""

    full_name: str = Field(min_length=1, max_length=70)
    participant_type: ParticipantType
    age: int
    bio: str | None = Field(default=None, max_length=500)
    skills: list[ParticipantSkillForm] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    contacts: list[ParticipantContactForm] = Field(default_factory=list, max_length=15)


@interactor
class UpdateParticipant:
    """Interactor for updating ``Participant`` profile."""

    uow: UoW
    idp: IdProvider
    participant_gateway: ParticipantGateway
    clock: Clock

    async def execute(self, data: UpdateParticipantForm) -> None:
        """Update participant profile fields."""
        user_id = await self.idp.get_user_id()
        participant = await self.participant_gateway.get_by_user_id(user_id, eager_skills_and_contacts=True)

        if participant is None:
            raise ParticipantNotFoundError

        logger.debug("Updating participant profile", user_id=user_id)

        participant.update(
            data=UpdateParticipantData(
                full_name=data.full_name,
                bio=data.bio,
                skills=ParticipantSkills([ParticipantSkill(name=s.name, level=s.level) for s in data.skills]),
                experience_level=data.experience_level,
                contacts=ParticipantContacts([ParticipantContact(title=c.title, value=c.value) for c in data.contacts]),
                participant_type=data.participant_type,
                age=Age(data.age),
            ),
            clock=self.clock,
        )
        await self.uow.commit()

        logger.info("Participant profile updated", user_id=user_id)
