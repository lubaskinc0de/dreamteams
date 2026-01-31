from datetime import UTC, datetime
from typing import override

from dreamteams.entities.common.clock import Clock


class SystemClock(Clock):
    """System clock implementation that returns current UTC time."""

    @override
    def now(self) -> datetime:
        """Get current datetime in UTC."""
        return datetime.now(tz=UTC)
