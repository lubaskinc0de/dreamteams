from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class ServerConfig:
    """HTTP-server configuration."""

    server_port: int
    server_host: str
    workers: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ServerTomlConfig:
    """HTTP-server configuration fields supplied via TOML (host/port remain env-only)."""

    workers: int


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
