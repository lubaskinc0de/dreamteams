from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import User


class UserGateway(Protocol):
    """Protocol defining the interface for reading user data from persistent storage."""

    @abstractmethod
    async def get(self, user_id: UserId) -> User | None:
        """Retrieves a bare user entity by ID. Relationships (organizer/participant) are not loaded."""
        raise NotImplementedError
