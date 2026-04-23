import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from dreamteams_common.observability.config import OTelConfig
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.db.config import DbConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.bootstrap.config.sentry import SentryConfig
from dreamteams_exporter.bootstrap.config.server import ServerConfig

_CONFIG_PATH_ENV = "EXPORTER_CONFIG_PATH"
_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    """Fully-loaded exporter configuration, read once from TOML at bootstrap."""

    db: DbConfig
    cache: CacheConfig
    nats: NatsConfig
    s3: S3Config
    dreamteams_api: DreamteamsApiConfig
    server: ServerConfig
    otel: OTelConfig
    sentry: SentryConfig

    @classmethod
    def load(cls) -> Self:
        """Loads the exporter TOML config pointed at by ``EXPORTER_CONFIG_PATH``."""
        config_path = os.environ.get(_CONFIG_PATH_ENV)
        if config_path is None:
            msg = f"'{_CONFIG_PATH_ENV}' must point at the exporter TOML config"
            raise RuntimeError(msg)

        with Path(config_path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data, cls)
