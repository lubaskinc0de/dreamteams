from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort
from sqlalchemy import URL

EXPORTER_SCHEMA = "exporter"

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class DbConfig:
    """Exporter database connection configuration — fully populated from TOML."""

    user: str
    password: str
    host: str
    port: int
    name: str
    pool_size: int = 5
    max_overflow: int = 5

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[db]`` section of the given TOML file into a DbConfig."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["db"], cls)

    @property
    def connection_url(self) -> URL:
        """Builds the asyncpg SQLAlchemy URL for the exporter."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )
