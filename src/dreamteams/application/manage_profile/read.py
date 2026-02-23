import structlog
from pydantic import BaseModel

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import OrganizerId, UserId

logger: Logger = structlog.get_logger(__name__)


class OrganizerModel(BaseModel):
    """Response model containing the info about ``Organizer``."""

    id: OrganizerId
    user_id: UserId
    organizer_name: str
    phone_number: str
    contact_email: str


class ProfileModel(BaseModel):
    """Response model containing the info about user profile."""

    user_id: UserId
    organizer: OrganizerModel | None
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
        user = await self.idp.get_user()
        logger.debug("Reading user profile", user_id=user.id)

        if not user.is_admin:
            organizer = user.get_role()
            organizer_model = OrganizerModel(
                id=organizer.id,
                user_id=organizer.user_id,
                organizer_name=organizer.organizer_name,
                phone_number=organizer.phone_number,
                contact_email=organizer.contact_email,
            )
        else:
            organizer_model = None

        return ProfileModel(
            user_id=user.id,
            organizer=organizer_model,
            avatar_url=self.avatar_storage.get_url(user.avatar) if user.avatar is not None else None,
            is_admin=user.is_admin,
        )
