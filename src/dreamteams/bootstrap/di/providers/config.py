from dishka import BaseScope, Provider, Scope, from_context

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.tracing import TracingConfig
from dreamteams.bootstrap.config.loader import Config


class ConfigProvider(Provider):
    """Dishka provider that exposes configuration objects from the context."""

    scope: BaseScope | None = Scope.APP
    configs = (
        from_context(Config)
        + from_context(DbConfig)
        + from_context(WebAuthUserIdProviderConfig)
        + from_context(TracingConfig)
        + from_context(S3Config)
    )
