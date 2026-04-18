from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.env_loader import env, optional_env
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register.register_superuser import SuperuserConfig
from dreamteams.bootstrap.observability import OTelConfig
from dreamteams.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig

retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class TomlConfig:
    """Configuration structure loaded from TOML file matching the file's schema."""

    auth: WebAuthUserIdProviderConfig
    otel: OTelConfig
    cors: CorsConfig
    api: ApiConfig


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

    @classmethod
    def load(cls) -> Self:
        """Loads configuration."""
        config_path = env("CONFIG_PATH", Path)

        with config_path.open("rb") as f:
            toml_config = retort.load(toml_rs.load(f), TomlConfig)

        db = DbConfig.from_env()
        server = ServerConfig(
            server_port=env("SERVER_PORT", int),
            server_host=env("SERVER_HOST"),
            workers=optional_env("SERVER_WORKERS", int) or 1,
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
        )
