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

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[dreamteams_api]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["dreamteams_api"], cls)
