import structlog
from pydantic import BaseModel

from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import OrganizerId, UserId
from dreamteams.entities.organizer import Logo

logger: Logger = structlog.get_logger(__name__)


class OrganizerModel(BaseModel):
    """Response model containing the info about ``Organizer``."""

    id: OrganizerId
    user_id: UserId
    organizer_name: str
    phone_number: str
    contact_email: str
    logo: Logo | None


class ProfileModel(BaseModel):
    """Response model containing the info about user profile."""

    user_id: UserId
    organizer: OrganizerModel | None


@interactor
class ViewProfile:
    """Interactor for viewing user profile."""

    uow: UoW
    idp: IdProvider

    async def execute(self) -> ProfileModel:
        """View user profile."""
        user = await self.idp.get_user()
        logger.debug("Viewing user profile", user_id=user.id)

        organizer = user.get_role()
        organizer_model = OrganizerModel(
            id=organizer.id,
            user_id=organizer.user_id,
            organizer_name=organizer.organizer_name,
            phone_number=organizer.phone_number,
            contact_email=organizer.contact_email,
            logo=organizer.logo,
        )

        return ProfileModel(user_id=user.id, organizer=organizer_model)
