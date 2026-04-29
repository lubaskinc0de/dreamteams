import structlog
from pydantic import BaseModel, EmailStr, Field

from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.organizer import OrganizerAlreadyExistsError, OrganizerNotFoundError
from dreamteams.entities.user import UpdateOrganizerData
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class UpdateOrganizerForm(BaseModel):
    """Form for updating ``Organizer`` profile."""

    organizer_name: str = Field(max_length=70)
    contact_email: EmailStr


@interactor
class UpdateOrganizer:
    """Interactor for updating ``Organizer`` profile."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway

    async def execute(self, data: UpdateOrganizerForm) -> None:
        """Update organizer profile fields."""
        user_id = await self.idp.get_user_id()
        organizer = await self.organizer_gateway.get_by_user_id(user_id)

        if organizer is None:
            raise OrganizerNotFoundError

        logger.debug("Updating organizer profile", user_id=user_id)

        email_changed = data.contact_email != organizer.contact_email
        if email_changed and not await self.organizer_gateway.is_unique_by_email(data.contact_email):
            raise OrganizerAlreadyExistsError

        organizer.update(
            UpdateOrganizerData(
                organizer_name=data.organizer_name,
                contact_email=data.contact_email,
            ),
        )
        await self.uow.commit()

        logger.info("Organizer profile updated", user_id=user_id)
