from datetime import UTC, datetime
from typing import Protocol, override


class Clock(Protocol):
    """Protocol for getting current time."""

    def now(self) -> datetime:
        """Get current datetime in UTC."""


class SystemClock(Clock):
    """System clock implementation that returns current UTC time."""

    @override
    def now(self) -> datetime:
        """Get current datetime in UTC."""
        return datetime.now(tz=UTC)
