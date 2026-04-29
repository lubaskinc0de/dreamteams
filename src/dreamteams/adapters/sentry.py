from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class SentryConfig:
    """A config for sentry."""

    dsn: str | None = None
