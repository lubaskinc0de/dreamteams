import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register_user.register_superuser import SuperuserConfig
from dreamteams.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig
from dreamteams_common.observability.config import OTelConfig

_CONFIG_PATH_ENV = "APP_CONFIG_PATH"
_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    """Fully-loaded main application configuration, read once from TOML at bootstrap."""

    db: DbConfig
    auth: WebAuthUserIdProviderConfig
    otel: OTelConfig
    server: ServerConfig
    cors: CorsConfig
    api: ApiConfig
    s3: S3Config
    superuser: SuperuserConfig
    sentry: SentryConfig
    cache: CacheConfig

    @classmethod
    def load(cls) -> Self:
        """Loads the main app TOML config pointed at by ``APP_CONFIG_PATH``."""
        config_path = os.environ.get(_CONFIG_PATH_ENV)
        if config_path is None:
            msg = f"'{_CONFIG_PATH_ENV}' must point at the main app TOML config"
            raise RuntimeError(msg)

        with Path(config_path).open("rb") as fh:
            data = toml_rs.load(fh)

        return _retort.load(data, cls)
