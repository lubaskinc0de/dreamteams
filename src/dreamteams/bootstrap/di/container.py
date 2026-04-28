from dishka import STRICT_VALIDATION, AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register_user.register_superuser import SuperuserConfig
from dreamteams.bootstrap.config.loader import Config
from dreamteams.bootstrap.di.providers.adapter import AdapterProvider
from dreamteams.bootstrap.di.providers.config import ConfigProvider
from dreamteams.bootstrap.di.providers.interactor import InteractorProvider
from dreamteams.bootstrap.di.providers.metrics import MetricsProvider
from dreamteams.presentation.fast_api.config import ServerConfig
from dreamteams_common.observability.config import OTelConfig


def get_async_container(config: Config) -> AsyncContainer:
    """Creates and configures the async DI container with all providers and initial context values."""
    providers = [
        ConfigProvider(),
        FastapiProvider(),
        AdapterProvider(),
        MetricsProvider(),
        InteractorProvider(),
    ]
    context = {
        Config: config,
        DbConfig: config.db,
        WebAuthUserIdProviderConfig: config.auth,
        S3Config: config.s3,
        SuperuserConfig: config.superuser,
        SentryConfig: config.sentry,
        OTelConfig: config.otel,
        ServerConfig: config.server,
        CacheConfig: config.cache,
    }
    container = make_async_container(*providers, context=context, validation_settings=STRICT_VALIDATION)
    return container
