from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.identifiers import OrganizerId, UserId

type Avatar = str


@model
class Organizer(Entity):
    """The organization that hosts competitions."""

    id: OrganizerId
    user_id: UserId
    organizer_name: str
    phone_number: str
    contact_email: str
    avatar: Avatar | None
