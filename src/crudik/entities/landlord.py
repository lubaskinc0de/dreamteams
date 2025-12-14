from crudik.entities.base import Entity, model
from crudik.entities.common.identifiers import LandlordId, UserId


@model
class Landlord(Entity):
    """The person who rents out the property."""

    id: LandlordId
    user_id: UserId
    landlord_name: str
    phone_number: str
