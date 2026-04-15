from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SentryConfig:
    """A config for sentry."""

    dsn: str | None
