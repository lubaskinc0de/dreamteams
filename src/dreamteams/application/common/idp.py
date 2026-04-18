from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId


class IdProvider(Protocol):
    """Protocol for retrieving the identifier of the currently authenticated user from the request context."""

    @abstractmethod
    async def get_user_id(self) -> UserId:
        """Returns the UserId of the currently authenticated user; raises ``UnauthorizedError`` otherwise."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_id_or_none(self) -> UserId | None:
        """Returns the UserId of the currently authenticated user, or ``None`` if the request is unauthenticated."""
        raise NotImplementedError
