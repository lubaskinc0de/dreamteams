from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.errors.organizer import (
    OrganizerUserIdMismatchError,
    UserAlreadyOrganizerError,
)
from dreamteams.entities.organizer import Organizer

type Avatar = str


@model
class User(Entity):
    """Domain entity representing a user in the application.

    Contains roles such as ``organizer`` and ``participant``.
    """

    id: UserId
    organizer: Organizer | None
    avatar: Avatar | None = None

    def make_organizer(self, organizer: Organizer) -> None:
        """Attach ``Organizer`` role to user."""
        if self.organizer is not None:
            raise UserAlreadyOrganizerError

        if organizer.user_id != self.id:
            raise OrganizerUserIdMismatchError

        self.organizer = organizer

    def get_role(self) -> Organizer:
        """Get user role."""
        if self.organizer is not None:
            return self.organizer
        msg = "User has no attached role"
        raise ValueError(msg)


def user_factory(user_id: UserId) -> User:
    """``User`` entity factory (user created without roles)."""
    return User(user_id, organizer=None)
