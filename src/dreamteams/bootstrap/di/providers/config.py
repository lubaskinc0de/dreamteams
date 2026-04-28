from dishka import BaseScope, Provider, Scope, from_context

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register_user.register_superuser import SuperuserConfig
from dreamteams.bootstrap.config_loader import Config
from dreamteams.presentation.fast_api.config import ServerConfig
from dreamteams_common.observability.config import OTelConfig


class ConfigProvider(Provider):
    """Dishka provider that exposes configuration objects from the context."""

    scope: BaseScope | None = Scope.APP
    configs = (
        from_context(Config)
        + from_context(DbConfig)
        + from_context(WebAuthUserIdProviderConfig)
        + from_context(S3Config)
        + from_context(SuperuserConfig)
        + from_context(SentryConfig)
        + from_context(OTelConfig)
        + from_context(ServerConfig)
        + from_context(CacheConfig)
    )
