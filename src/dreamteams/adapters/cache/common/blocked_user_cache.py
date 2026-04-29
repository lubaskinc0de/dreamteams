from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus


class BlockedUserCache(Protocol):
    """Adapter-local read/write interface for the blocked-user cache."""

    @abstractmethod
    async def get_ban_status(self, user_id: UserId) -> BanStatus | None:
        """Return BanStatus(is_blocked=True, ...) if cached, None on miss or error."""
        raise NotImplementedError

    @abstractmethod
    async def set_blocked(self, user_id: UserId, ban_status: BanStatus) -> None:
        """Cache the ban status for a blocked user."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Remove the user from the blocked cache."""
        raise NotImplementedError
