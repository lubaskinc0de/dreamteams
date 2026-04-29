from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.entities.user import User


class IdProvider(Protocol):
    """Resolves the caller's identity for the current request."""

    @abstractmethod
    async def get_user(self) -> User:
        """Returns the authenticated User; raises UnauthorizedError if no identity is attached to the request."""
        raise NotImplementedError
