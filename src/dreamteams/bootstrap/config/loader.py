from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.env_loader import env
from dreamteams.adapters.tracing import TracingConfig
from dreamteams.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig

retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class TomlConfig:
    """Configuration structure loaded from TOML file matching the file's schema."""

    auth: WebAuthUserIdProviderConfig
    tracing: TracingConfig
    cors: CorsConfig
    api: ApiConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    """Main application configuration."""

    db: DbConfig
    web_auth_user_id_provider: WebAuthUserIdProviderConfig
    tracing: TracingConfig
    server: ServerConfig
    cors: CorsConfig
    api: ApiConfig
    s3: S3Config

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
        )
        s3 = S3Config(
            bucket_name=env("S3_BUCKET_NAME"),
            endpoint_url=env("S3_ENDPOINT_URL"),
            access_key=env("S3_ACCESS_KEY"),
            secret_key=env("S3_SECRET_KEY"),
            region=env("S3_REGION"),
        )
        return cls(
            db=db,
            web_auth_user_id_provider=toml_config.auth,
            tracing=toml_config.tracing,
            server=server,
            cors=toml_config.cors,
            api=toml_config.api,
            s3=s3,
        )
