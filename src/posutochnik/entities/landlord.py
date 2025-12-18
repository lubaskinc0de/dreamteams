from posutochnik.entities.base import Entity, model
from posutochnik.entities.common.identifiers import LandlordId, UserId

type Avatar = str


@model
class Landlord(Entity):
    """The person who rents out the property."""

    id: LandlordId
    user_id: UserId
    landlord_name: str
    phone_number: str
    contact_email: str
    avatar: Avatar | None
