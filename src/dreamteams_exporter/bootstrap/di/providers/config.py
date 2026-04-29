from dishka import BaseScope, Provider, Scope, from_context

from dreamteams_common.observability.config import OTelConfig
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.bootstrap.config.loader import Config
from dreamteams_exporter.bootstrap.config.sentry import SentryConfig
from dreamteams_exporter.bootstrap.config.server import ServerConfig


class ConfigProvider(Provider):
    """Exposes every ``Config`` sub-section as an APP-scoped dependency."""

    scope: BaseScope | None = Scope.APP

    configs = (
        from_context(Config)
        + from_context(CacheConfig)
        + from_context(NatsConfig)
        + from_context(S3Config)
        + from_context(DreamteamsApiConfig)
        + from_context(ServerConfig)
        + from_context(OTelConfig)
        + from_context(SentryConfig)
    )
