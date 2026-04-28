from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.db.config import DbConfig, DbPoolTomlConfig
from dreamteams.adapters.env_loader import env, optional_env
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register_user.register_superuser import SuperuserConfig
from dreamteams.bootstrap.observability import OTelConfig
from dreamteams.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig, ServerTomlConfig

retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class TomlConfig:
    """Configuration structure loaded from TOML file matching the file's schema."""

    auth: WebAuthUserIdProviderConfig
    otel: OTelConfig
    cors: CorsConfig
    api: ApiConfig
    server: ServerTomlConfig
    db: DbPoolTomlConfig
    cache: CacheConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    """Main application configuration."""

    db: DbConfig
    web_auth_user_id_provider: WebAuthUserIdProviderConfig
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
        """Loads configuration."""
        config_path = env("CONFIG_PATH", Path)

        with config_path.open("rb") as f:
            toml_config = retort.load(toml_rs.load(f), TomlConfig)

        db = DbConfig.from_env(
            max_total_pool_size=toml_config.db.max_total_pool_size,
            max_total_overflow=toml_config.db.max_total_overflow,
        )
        server = ServerConfig(
            server_port=env("SERVER_PORT", int),
            server_host=env("SERVER_HOST"),
            workers=toml_config.server.workers,
        )
        s3 = S3Config(
            bucket_name=env("S3_BUCKET_NAME"),
            endpoint_url=env("S3_ENDPOINT_URL"),
            access_key=env("S3_ACCESS_KEY"),
            secret_key=env("S3_SECRET_KEY"),
            region=env("S3_REGION"),
            public_url=env("S3_PUBLIC_URL"),
        )
        superuser = SuperuserConfig(password_hash=env("SUPERUSER_PWD_HASH"))
        sentry = SentryConfig(optional_env("SENTRY_DSN"))
        return cls(
            db=db,
            web_auth_user_id_provider=toml_config.auth,
            otel=toml_config.otel,
            server=server,
            cors=toml_config.cors,
            api=toml_config.api,
            s3=s3,
            superuser=superuser,
            sentry=sentry,
            cache=toml_config.cache,
        )
