from dataclasses import dataclass
from typing import Self

from sqlalchemy import URL

from dreamteams.adapters.env_loader import env


@dataclass(slots=True, frozen=True, kw_only=True)
class DbPoolTomlConfig:
    """Pool sizing expressed as collective caps across all API workers.

    Per-worker ``pool_size`` and ``max_overflow`` are derived at engine-build time by
    dividing these totals by ``server.workers``. The total ``max_total_pool_size +
    max_total_overflow`` must stay below pgbouncer's DEFAULT_POOL_SIZE to avoid
    client-side queueing.
    """

    max_total_pool_size: int
    max_total_overflow: int


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
    def from_env(cls, *, max_total_pool_size: int, max_total_overflow: int) -> Self:
        """Creates database configuration by reading connection parameters from environment variables."""
        return cls(
            user=env("DB_USER"),
            password=env("DB_PASSWORD"),
            host=env("DB_HOST"),
            port=env("DB_PORT", int),
            db_name=env("DB_NAME"),
            max_total_pool_size=max_total_pool_size,
            max_total_overflow=max_total_overflow,
        )

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
