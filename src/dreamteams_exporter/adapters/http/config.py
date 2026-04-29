from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class DreamteamsApiConfig:
    """Configuration for outbound HTTP calls back to the main dreamteams context."""

    base_url: str
    auth_header_name: str
    timeout_seconds: float
    connect_timeout_seconds: float | None = None
    sock_connect_timeout_seconds: float | None = None
    sock_read_timeout_seconds: float | None = None
    retry_attempts: int = 3
    retry_backoff_base_seconds: float = 0.1
    retry_backoff_max_seconds: float = 1.0

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[dreamteams_api]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["dreamteams_api"], cls)
