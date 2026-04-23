from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class NatsConfig:
    """NATS broker configuration for both publisher and consumer."""

    url: str
    stream_name: str = "exporter"
    process_subject: str = "exporter.jobs.process"
    process_consumer: str = "exporter-worker"

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[nats]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["nats"], cls)
