from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class ServerConfig:
    """HTTP-server configuration."""

    server_port: int
    server_host: str


@dataclass(slots=True, frozen=True, kw_only=True)
class CorsConfig:
    """HTTP CORS policy config."""

    allow_origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]


@dataclass(slots=True, frozen=True, kw_only=True)
class ApiConfig:
    """HTTP api config."""

    root_path: str
