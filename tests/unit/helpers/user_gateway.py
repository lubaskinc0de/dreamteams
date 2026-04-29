"""Gateway for User entity construction in unit tests."""

from dataclasses import dataclass

from dreamteams.entities.user import User
from tests.common.factory.entities.user import UserFactory


@dataclass
class UserGateway:
    """Gateway for building User entities."""

    user_factory: type[UserFactory]

    def create(self, *, is_admin: bool = False) -> User:
        """Build a fresh User without attached roles."""
        return self.user_factory.build(is_admin=is_admin)

    def create_admin(self) -> User:
        """Build a fresh admin User."""
        return self.user_factory.build(is_admin=True)
