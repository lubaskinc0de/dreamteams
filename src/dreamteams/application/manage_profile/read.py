import structlog
from pydantic import BaseModel

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import OrganizerId, ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import ExperienceLevel

logger: Logger = structlog.get_logger(__name__)


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
    user_gateway: UserGateway
    organizer_gateway: OrganizerGateway
    participant_gateway: ParticipantGateway
    avatar_storage: AvatarStorage

    async def execute(self) -> ProfileModel:
        """Read user profile."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        participant = await self.participant_gateway.get_by_user_id(user_id, eager_skills_and_contacts=True)
        logger.debug("Reading user profile", user_id=user_id)

        organizer_model = (
            OrganizerModel(
                id=organizer.id,
                user_id=organizer.user_id,
                organizer_name=organizer.organizer_name,
                phone_number=organizer.phone_number,
                contact_email=organizer.contact_email,
            )
            if organizer is not None
            else None
        )

        participant_model = (
            ParticipantModel(
                id=participant.id,
                user_id=participant.user_id,
                full_name=participant.full_name,
                participant_type=participant.participant_type,
                age=participant.age.value,
                bio=participant.bio,
                skills=participant.skills,
                experience_level=participant.experience_level,
                preferred_domains=participant.preferred_domains,
                contacts=participant.contacts,
            )
            if participant is not None
            else None
        )

        return ProfileModel(
            user_id=user.id,
            organizer=organizer_model,
            participant=participant_model,
            avatar_url=self.avatar_storage.get_url(user.avatar) if user.avatar is not None else None,
            is_admin=user.is_admin,
        )
