from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class SentryConfig:
    """Sentry DSN for the exporter — ``dsn = None`` disables the integration."""

    dsn: str | None = None

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[sentry]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data.get("sentry", {}), cls)
