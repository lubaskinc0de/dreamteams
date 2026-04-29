from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class ServerConfig:
    """Binding parameters for the exporter's internal FastAPI surface."""

    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 1

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[server]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data.get("server", {}), cls)
