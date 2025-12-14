from crudik.entities.base import Entity, model
from crudik.entities.common.identifiers import UserId
from crudik.entities.errors.landlord import LandlordUserIdMismatchError, UserAlreadyLandlordError
from crudik.entities.landlord import Landlord


@model
class User(Entity):
    """Domain entity representing a user in the application. Contains roles such as ``landlord`` and ``tenant``."""

    id: UserId
    landlord: Landlord | None

    def attach_landlord(self, landlord: Landlord) -> None:
        """Attach ``Landlord`` role to user."""
        if self.landlord is not None:
            raise UserAlreadyLandlordError

        if landlord.user_id != self.id:
            raise LandlordUserIdMismatchError

        self.landlord = landlord


def create_new_user(user_id: UserId) -> User:
    """Create new user in the system."""
    return User(user_id, landlord=None)
