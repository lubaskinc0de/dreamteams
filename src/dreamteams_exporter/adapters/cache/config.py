from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class CacheConfig:
    """Redis-backed cache + rate-limit configuration for the exporter."""

    url: str
    rate_limit_window_seconds: int = 3600
    rate_limit_max: int = 10

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[cache]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["cache"], cls)
