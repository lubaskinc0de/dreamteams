from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

from posutochnik.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from posutochnik.adapters.db.config import DbConfig
from posutochnik.adapters.env_loader import env
from posutochnik.adapters.tracing import TracingConfig
from posutochnik.entities import config
from posutochnik.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig

retort = Retort()


@config
class TomlConfig:
    """Configuration structure loaded from TOML file matching the file's schema."""

    auth: WebAuthUserIdProviderConfig
    tracing: TracingConfig
    cors: CorsConfig
    api: ApiConfig


@config
class Config:
    """Main application configuration."""

    db: DbConfig
    web_auth_user_id_provider: WebAuthUserIdProviderConfig
    tracing: TracingConfig
    server: ServerConfig
    cors: CorsConfig
    api: ApiConfig

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
        return cls(
            db=db,
            web_auth_user_id_provider=toml_config.auth,
            tracing=toml_config.tracing,
            server=server,
            cors=toml_config.cors,
            api=toml_config.api,
        )
