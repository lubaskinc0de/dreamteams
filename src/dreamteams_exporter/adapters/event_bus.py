from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import override

import structlog

from dreamteams_common.logger import Logger
from dreamteams_exporter.application.common.event_bus import EventBus
from dreamteams_exporter.application.common.events import DomainEvent

type EventHandler = Callable[[DomainEvent], Awaitable[None]]

logger: Logger = structlog.get_logger(__name__)


class InMemoryEventBus(EventBus):
    """Synchronous in-process event bus for adapter-side exporter event handlers."""

    def __init__(self, handlers: Mapping[type[DomainEvent], Sequence[EventHandler]]) -> None:
        self._handlers = handlers

    @override
    async def publish(self, event: DomainEvent) -> None:
        """Dispatch the event to handlers registered for its exact event type."""
        for handler in self._handlers.get(type(event), ()):
            try:
                await handler(event)
            except Exception:  # noqa: BLE001
                logger.warning("exporter domain event handler failed", exc_info=True, domain_event=event)
