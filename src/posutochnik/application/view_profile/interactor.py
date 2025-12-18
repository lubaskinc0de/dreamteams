import structlog
from pydantic import BaseModel

from posutochnik.application.common.idp import IdProvider
from posutochnik.application.common.interactor import interactor
from posutochnik.application.common.logger import Logger
from posutochnik.application.common.uow import UoW
from posutochnik.entities.common.identifiers import LandlordId, UserId
from posutochnik.entities.landlord import Avatar

logger: Logger = structlog.get_logger(__name__)


class LandlordModel(BaseModel):
    """Response model containing the info about ``Landlord``."""

    id: LandlordId
    user_id: UserId
    landlord_name: str
    phone_number: str
    contact_email: str
    avatar: Avatar | None


class ProfileModel(BaseModel):
    """Response model containing the info about user profile."""

    user_id: UserId
    landlord: LandlordModel | None


@interactor
class ViewProfile:
    """Interactor for viewing user profile."""

    uow: UoW
    idp: IdProvider

    async def execute(self) -> ProfileModel:
        """View user profile."""
        user = await self.idp.get_user()
        logger.debug("Viewing user profile", user_id=user.id)

        landlord = user.get_role()
        landlord_model = LandlordModel(
            id=landlord.id,
            user_id=landlord.user_id,
            landlord_name=landlord.landlord_name,
            phone_number=landlord.phone_number,
            contact_email=landlord.contact_email,
            avatar=landlord.avatar,
        )

        return ProfileModel(user_id=user.id, landlord=landlord_model)
