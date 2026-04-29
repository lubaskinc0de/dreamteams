import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort
from sqlalchemy import URL

_CONFIG_PATH_ENV = "APP_CONFIG_PATH"
_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class DbConfig:
    """Database connection configuration parameters."""

    user: str
    password: str
    host: str
    port: int
    db_name: str
    # Collective per-process caps shared across all API workers. At runtime each worker
    # gets ``max_total_pool_size // workers`` pool slots plus ``max_total_overflow // workers``
    # overflow slots. Sum across workers must stay below pgbouncer's DEFAULT_POOL_SIZE to
    # avoid client-side queueing.
    max_total_pool_size: int
    max_total_overflow: int

    @classmethod
    def load(cls) -> Self:
        """Loads the ``[db]`` section from the TOML config pointed at by ``APP_CONFIG_PATH``."""
        config_path = os.environ.get(_CONFIG_PATH_ENV)
        if config_path is None:
            msg = f"'{_CONFIG_PATH_ENV}' must point at the main app TOML config"
            raise RuntimeError(msg)

        with Path(config_path).open("rb") as fh:
            data = toml_rs.load(fh)

        return _retort.load(data["db"], cls)

    @property
    def connection_url(self) -> URL:
        """Constructs and returns the SQLAlchemy asyncpg connection URL string for database connections."""
        user = self.user
        password = self.password
        host = self.host
        port = self.port
        db_name = self.db_name

        return URL.create(
            drivername="postgresql+asyncpg",
            username=user,
            password=password,
            port=port,
            host=host,
            database=db_name,
        )
