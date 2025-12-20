from dreamteams.entities.common.config import config


@config
class ServerConfig:
    """HTTP-server configuration."""

    server_port: int
    server_host: str


@config
class CorsConfig:
    """HTTP CORS policy config."""

    allow_origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]


@config
class ApiConfig:
    """HTTP api config."""

    root_path: str
