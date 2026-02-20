from uuid import uuid4

import structlog
from pydantic import BaseModel, EmailStr, Field

from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.phone_number import RussianPhoneNumber
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.invite import InviteNotFoundError
from dreamteams.application.errors.organizer import OrganizerAlreadyExistsError
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.entities.common.identifiers import OrganizerId, UserId
from dreamteams.entities.user import Organizer

logger: Logger = structlog.get_logger(__name__)


class CreatedOrganizer(BaseModel):
    """Response model containing the info about newly created ``Organizer`` and ``User``."""

    organizer_id: OrganizerId
    user_id: UserId


class OrganizerForm(BaseModel):
    """Form for registering as ``Organizer``."""

    organizer_name: str = Field(max_length=70)
    phone_number: RussianPhoneNumber
    contact_email: EmailStr
    invite_code: str


@interactor
class RegisterOrganizer:
    """Interactor for registering as ``Organizer``."""

    uow: UoW
    user_factory: UserFactory
    organizer_gateway: OrganizerGateway
    organizer_invite_gateway: OrganizerInviteGateway

    async def execute(self, data: OrganizerForm) -> CreatedOrganizer:
        """Creates a new ``User`` and ``Organizer`` role."""
        logger.debug("Registering as organizer", **data.model_dump(exclude={"invite_code"}))

        invite = await self.organizer_invite_gateway.get_by_code(data.invite_code)
        if invite is None:
            logger.warning("Invite not found during organizer registration")
            raise InviteNotFoundError

        invite.use()

        # Check if organizer with same phone number or email already exists
        is_unique = await self.organizer_gateway.is_unique(data.phone_number, data.contact_email)
        if not is_unique:
            logger.warning(
                "Attempt to register organizer with existing credentials",
                phone_number=data.phone_number,
                contact_email=data.contact_email,
            )
            raise OrganizerAlreadyExistsError

        user = await self.user_factory.create_user()
        organizer_id = uuid4()
        logger.debug("Generated new organizer id", user_id=user.id, organizer_id=organizer_id)
        organizer = Organizer(
            id=organizer_id,
            user_id=user.id,
            user=user,
            organizer_name=data.organizer_name,
            phone_number=data.phone_number,
            contact_email=data.contact_email,
        )
        logger.debug("Creating role 'Organizer' for user", user_id=user.id)
        user.make_organizer(organizer)

        self.uow.add(organizer)
        await self.uow.commit()

        logger.info("Organizer created", organizer=organizer)
        return CreatedOrganizer(organizer_id=organizer_id, user_id=user.id)
