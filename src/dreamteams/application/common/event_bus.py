from abc import abstractmethod
from typing import Protocol

from dreamteams.application.common.events import DomainEvent


class EventBus(Protocol):
    """Publishes domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        raise NotImplementedError
