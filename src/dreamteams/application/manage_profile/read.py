import structlog
from opentelemetry import trace
from pydantic import BaseModel

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import OrganizerId, ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import ExperienceLevel

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


class OrganizerModel(BaseModel):
    """Response model containing the info about ``Organizer``."""

    id: OrganizerId
    user_id: UserId
    organizer_name: str
    phone_number: str
    contact_email: str


class ParticipantModel(BaseModel):
    """Response model containing the info about ``Participant``."""

    id: ParticipantId
    user_id: UserId
    full_name: str
    participant_type: ParticipantType
    age: int
    bio: str | None
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel | None
    preferred_domains: list[Domain]
    contacts: list[ParticipantContact]


class ProfileModel(BaseModel):
    """Response model containing the info about user profile."""

    user_id: UserId
    organizer: OrganizerModel | None
    participant: ParticipantModel | None
    avatar_url: str | None
    is_admin: bool


@interactor
class ReadProfile:
    """Interactor for reading user profile."""

    uow: UoW
    idp: IdProvider
    avatar_storage: AvatarStorage

    async def execute(self) -> ProfileModel:
        """Read user profile."""
        with _tracer.start_as_current_span("interactor.read_profile"):
            user = await self.idp.get_user()
            logger.debug("Reading user profile", user_id=user.id)

            if user.organizer is not None:
                organizer_model = OrganizerModel(
                    id=user.organizer.id,
                    user_id=user.organizer.user_id,
                    organizer_name=user.organizer.organizer_name,
                    phone_number=user.organizer.phone_number,
                    contact_email=user.organizer.contact_email,
                )
            else:
                organizer_model = None

            if user.participant is not None:
                participant_model = ParticipantModel(
                    id=user.participant.id,
                    user_id=user.participant.user_id,
                    full_name=user.participant.full_name,
                    participant_type=user.participant.participant_type,
                    age=user.participant.age.value,
                    bio=user.participant.bio,
                    skills=user.participant.skills,
                    experience_level=user.participant.experience_level,
                    preferred_domains=user.participant.preferred_domains,
                    contacts=user.participant.contacts,
                )
            else:
                participant_model = None

            return ProfileModel(
                user_id=user.id,
                organizer=organizer_model,
                participant=participant_model,
                avatar_url=self.avatar_storage.get_url(user.avatar) if user.avatar is not None else None,
                is_admin=user.is_admin,
            )
