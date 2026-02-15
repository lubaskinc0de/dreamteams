import structlog
from pydantic import BaseModel, EmailStr, Field

from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.phone_number import RussianPhoneNumber
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.organizer import OrganizerAlreadyExistsError, OrganizerNotFoundError
from dreamteams.entities.common.identifiers import OrganizerId

logger: Logger = structlog.get_logger(__name__)


class UpdateOrganizerForm(BaseModel):
    """Form for updating organizer profile."""

    organizer_name: str = Field (max_length=70)
    phone_number: RussianPhoneNumber
    contact_email: EmailStr

@interactor
class UpdateOrganizer:
    """Interactor for updating organizer profile."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway

    async def execute(self, organizer_id: OrganizerId, data: UpdateOrganizerForm) -> None:
        """Updates organizer profile."""
        logger.debug("Updating organizer profile", organizer_id=organizer_id, **data.model_dump(exclude_none=True))

        # Get current user
        user = await self.idp.get_user()

        # Get organizer
        organizer = await self.organizer_gateway.get(organizer_id)
        if organizer is None:
            logger.warning("Organizer not found", organizer_id=organizer_id, user_id=user.id)
            raise OrganizerNotFoundError

        # Check if user has permission to update this organizer
        if organizer.user_id != user.id:
            logger.warning(
                "User attempted to update organizer they don't own",
                user_id=user.id,
                organizer_id=organizer_id,
                organizer_user_id=organizer.user_id,
            )
            msg = "You can only update your own organizer profile"
            raise PermissionError(msg)

        # Check uniqueness if phone or email is being updated
        if data.phone_number is not None or data.contact_email is not None:
            is_unique = await self.organizer_gateway.is_unique(
                phone_number=data.phone_number or organizer.phone_number,
                contact_email=data.contact_email or organizer.contact_email,
                exclude_organizer_id=organizer_id,
            )
            if not is_unique:
                logger.warning(
                    "Attempt to update organizer with existing credentials",
                    phone_number=data.phone_number,
                    contact_email=data.contact_email,
                    organizer_id=organizer_id,
                )
                raise OrganizerAlreadyExistsError

        # Update fields if provided
        if data.organizer_name is not None:
            organizer.organizer_name = data.organizer_name

        if data.phone_number is not None:
            organizer.phone_number = data.phone_number

        if data.contact_email is not None:
            organizer.contact_email = data.contact_email

        # Add to UoW and commit
        self.uow.add(organizer)
        await self.uow.commit()

        logger.info(
            "Organizer profile updated",
            organizer_id=organizer_id,
            user_id=user.id,
            updated_fields=list(data.model_dump(exclude_none=True).keys()),
        )
