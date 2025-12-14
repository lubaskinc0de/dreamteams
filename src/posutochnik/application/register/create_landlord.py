from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

from posutochnik.application.common.idp import IdProvider
from posutochnik.application.common.interactor import interactor
from posutochnik.application.common.logger import Logger
from posutochnik.application.common.phone_number import RussianPhoneNumber
from posutochnik.application.common.uow import UoW
from posutochnik.entities.common.identifiers import LandlordId
from posutochnik.entities.landlord import Landlord

logger: Logger = structlog.get_logger(__name__)


class CreatedLandlord(BaseModel):
    """Response model containing the info about newly created landlord."""

    id: LandlordId


class LandlordForm(BaseModel):
    """Form for creating a new landlord."""

    landlord_name = Field(max_length=70)
    phone_number: RussianPhoneNumber


@interactor
class CreateLandlord:
    """Interactor for creating a new user entity."""

    uow: UoW
    idp: IdProvider

    async def execute(self, data: LandlordForm) -> CreatedLandlord:
        """Creates a new landlord."""
        logger.debug("Creating new landlord", **data.model_dump())
        user = await self.idp.get_user()

        landlord_id = uuid4()
        logger.debug("Generated new landlord id", user_id=user.id, landlord_id=landlord_id)
        landlord = Landlord(
            id=landlord_id,
            user_id=user.id,
            landlord_name=data.landlord_name,
            phone_number=data.phone_number,
            avatar=None,
        )
        logger.debug("Creating role 'Landlord' for user", user_id=user.id)
        user.attach_landlord(landlord)

        self.uow.add(landlord)
        await self.uow.commit()

        logger.info("Landlord created", landlord=landlord)
        return CreatedLandlord(id=landlord_id)
