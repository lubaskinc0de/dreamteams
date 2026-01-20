from datetime import UTC, datetime


class SystemClock:
    """System clock implementation that returns current UTC time."""

    def now(self) -> datetime:
        """Get current datetime in UTC."""
        return datetime.now(tz=UTC)
