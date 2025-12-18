from uuid import uuid4

import structlog
from pydantic import BaseModel, EmailStr, Field

from posutochnik.application.common.interactor import interactor
from posutochnik.application.common.logger import Logger
from posutochnik.application.common.phone_number import RussianPhoneNumber
from posutochnik.application.common.uow import UoW
from posutochnik.application.register.shared.user_factory import UserFactory
from posutochnik.entities.common.identifiers import LandlordId, UserId
from posutochnik.entities.landlord import Landlord

logger: Logger = structlog.get_logger(__name__)


class CreatedLandlord(BaseModel):
    """Response model containing the info about newly created ``Landlord`` and ``User``."""

    landlord_id: LandlordId
    user_id: UserId


class LandlordForm(BaseModel):
    """Form for registering as ``Landlord``."""

    landlord_name: str = Field(max_length=70)
    phone_number: RussianPhoneNumber
    contact_email: EmailStr


@interactor
class RegisterLandlord:
    """Interactor for registering as ``Landlord``."""

    uow: UoW
    user_factory: UserFactory

    async def execute(self, data: LandlordForm) -> CreatedLandlord:
        """Creates a new ``User`` and ``Landlord``."""
        logger.debug("Registering as landlord", **data.model_dump())
        user = await self.user_factory.create_user()

        landlord_id = uuid4()
        logger.debug("Generated new landlord id", user_id=user.id, landlord_id=landlord_id)
        landlord = Landlord(
            id=landlord_id,
            user_id=user.id,
            landlord_name=data.landlord_name,
            phone_number=data.phone_number,
            contact_email=data.contact_email,
            avatar=None,
        )
        logger.debug("Creating role 'Landlord' for user", user_id=user.id)
        user.attach_landlord(landlord)

        self.uow.add(landlord)
        await self.uow.commit()

        logger.info("Landlord created", landlord=landlord)
        return CreatedLandlord(landlord_id=landlord_id, user_id=user.id)
