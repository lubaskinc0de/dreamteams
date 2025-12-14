from dishka import BaseScope, Provider, Scope, from_context

from posutochnik.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from posutochnik.adapters.db.config import DbConfig
from posutochnik.adapters.tracing import TracingConfig
from posutochnik.bootstrap.config.loader import Config


class ConfigProvider(Provider):
    """Dishka provider that exposes configuration objects from the context."""

    scope: BaseScope | None = Scope.APP
    configs = (
        from_context(Config)
        + from_context(DbConfig)
        + from_context(WebAuthUserIdProviderConfig)
        + from_context(TracingConfig)
    )
