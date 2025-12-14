from abc import abstractmethod
from typing import Protocol

from posutochnik.entities.common.identifiers import UserId
from posutochnik.entities.user import User


class UserGateway(Protocol):
    """Protocol defining the interface for reading user data from persistent storage."""

    @abstractmethod
    async def get(self, user_id: UserId) -> User | None:
        """Retrieves a user entity by its unique identifier, returns None if not found."""
        raise NotImplementedError
