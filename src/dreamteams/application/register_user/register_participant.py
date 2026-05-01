import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import MAX_PARTICIPANT_SKILLS, ParticipantSkillForm
from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import UserRegistered
from dreamteams.application.register_user.shared.user_factory import UserFactory
from dreamteams.entities.common.identifiers import ParticipantId, UserId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.participant.age import AGE_MAX, AGE_MIN, Age
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.participant_skill import ParticipantSkill
from dreamteams.entities.participant.participant_skills import ParticipantSkills
from dreamteams.entities.user import (
    ExperienceLevel,
    ParticipantData,
    participant_factory,
)
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)
EMAIL_CONTACT_TITLE = "Email"


class CreatedParticipant(BaseModel):
    """Response model containing the info about newly created ``Participant``."""

    participant_id: ParticipantId
    user_id: UserId


class ParticipantForm(BaseModel):
    """Form for registering as ``Participant``."""

    full_name: str = Field(min_length=1, max_length=70)
    participant_type: ParticipantType
    age: int = Field(ge=AGE_MIN, le=AGE_MAX)
    bio: str | None = Field(default=None, max_length=500)
    skills: list[ParticipantSkillForm] = Field(default_factory=list, max_length=MAX_PARTICIPANT_SKILLS)
    experience_level: ExperienceLevel | None = None
    contacts: list[ParticipantContactForm] = Field(default_factory=list, max_length=15)
    email: str | None = None


@interactor
class RegisterParticipant:
    """Interactor for registering as ``Participant``."""

    uow: UoW
    user_factory: UserFactory
    clock: Clock
    event_bus: EventBus

    async def execute(self, data: ParticipantForm) -> CreatedParticipant:
        """Creates a new ``User`` and ``Participant`` role."""
        logger.debug("Registering as participant", **data.model_dump())

        user = await self.user_factory.create_user()
        contacts = [ParticipantContact(title=c.title, value=c.value) for c in data.contacts]
        email = data.email.strip() if data.email is not None else None
        if email:
            contacts.append(ParticipantContact(title=EMAIL_CONTACT_TITLE, value=email))

        participant_data = ParticipantData(
            full_name=data.full_name,
            bio=data.bio,
            skills=ParticipantSkills(
                [
                    ParticipantSkill(
                        name=s.name,
                        level=s.level,
                    )
                    for s in data.skills
                ],
            ),
            experience_level=data.experience_level,
            contacts=ParticipantContacts(contacts),
            participant_type=data.participant_type,
            age=Age(data.age),
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
        await self.event_bus.publish(UserRegistered(role="participant"))

        logger.info(
            "Participant created",
            user_id=user.id,
            participant_id=participant.id,
        )

        return CreatedParticipant(
            participant_id=participant.id,
            user_id=user.id,
        )
