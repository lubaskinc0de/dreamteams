from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import User


class UserRoleFilter(Enum):
    """Role filter for admin-facing user lists."""

    ORGANIZER = "organizer"
    PARTICIPANT = "participant"


@dataclass(frozen=True, slots=True)
class UserListFilters:
    """Filters for admin-facing user lists."""

    search: str | None
    is_admin: bool | None
    is_blocked: bool | None
    role: UserRoleFilter | None


class UserGateway(Protocol):
    """Protocol defining the interface for reading user data from persistent storage."""

    @abstractmethod
    async def get(self, user_id: UserId) -> User | None:
        """Retrieves a bare user entity by ID. Relationships (organizer/participant) are not loaded."""
        raise NotImplementedError

    @abstractmethod
    async def get_with_roles(self, user_id: UserId) -> User | None:
        """Retrieves a user with organizer and participant relationships loaded, including blocked users."""
        raise NotImplementedError

    @abstractmethod
    async def list_with_roles(
        self,
        *,
        page: int,
        page_size: int,
        filters: UserListFilters,
    ) -> tuple[list[User], int]:
        """Return admin-facing users with role summaries and total count, including blocked users."""
        raise NotImplementedError
