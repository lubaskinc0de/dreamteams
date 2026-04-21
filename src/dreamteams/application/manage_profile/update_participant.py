import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.participant import ParticipantNotFoundError
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import ExperienceLevel, UpdateParticipantData

logger: Logger = structlog.get_logger(__name__)


class UpdateParticipantForm(BaseModel):
    """Form for updating ``Participant`` profile."""

    full_name: str = Field(min_length=1, max_length=70)
    participant_type: ParticipantType
    age: int
    bio: str | None = Field(default=None, max_length=500)
    skills: list[ParticipantSkillForm] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    preferred_domains: list[Domain] = Field(default_factory=list)
    contacts: list[ParticipantContactForm] = Field(default_factory=list)


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
                skills=[ParticipantSkill(name=s.name, level=s.level) for s in data.skills],
                experience_level=data.experience_level,
                preferred_domains=data.preferred_domains,
                contacts=[ParticipantContact(title=c.title, url=str(c.url)) for c in data.contacts],
                participant_type=data.participant_type,
                age=Age(data.age),
            ),
            clock=self.clock,
        )
        await self.uow.commit()

        logger.info("Participant profile updated", user_id=user_id)
