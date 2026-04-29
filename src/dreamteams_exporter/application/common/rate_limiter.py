from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.entities.common.identifiers import UserId


class ExportRateLimiter(Protocol):
    """Enforces a per-user cap on how many exports may run inside a rolling window."""

    @abstractmethod
    async def check_and_record(self, user_id: UserId) -> None:
        """Records one attempt for the user; raises RateLimitExceededError when over the configured cap."""
        raise NotImplementedError
