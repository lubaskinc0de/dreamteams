from polyfactory.factories import DataclassFactory

from dreamteams.entities.user import Avatar, Organizer, Participant, User


class UserFactory(DataclassFactory[User]):
    """Factory of User entities."""

    __model__ = User

    organizer: Organizer | None = None
    participant: Participant | None = None
    avatar: Avatar | None = None
    is_admin = False
