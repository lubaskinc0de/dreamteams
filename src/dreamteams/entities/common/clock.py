from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Protocol for getting current time."""

    def now(self) -> datetime:
        """Get current datetime in UTC."""
