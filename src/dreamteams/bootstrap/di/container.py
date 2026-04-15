from dishka import STRICT_VALIDATION, AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.adapters.tracing import TracingConfig
from dreamteams.application.register.register_superuser import SuperuserConfig
from dreamteams.bootstrap.config.loader import Config
from dreamteams.bootstrap.di.providers.adapter import AdapterProvider
from dreamteams.bootstrap.di.providers.config import ConfigProvider
from dreamteams.bootstrap.di.providers.interactor import InteractorProvider
from dreamteams.bootstrap.di.providers.tracing import HTTPTracingProvider


def get_async_container(config: Config) -> AsyncContainer:
    """Creates and configures the async DI container with all providers and initial context values."""
    providers = [
        ConfigProvider(),
        FastapiProvider(),
        AdapterProvider(),
        InteractorProvider(),
        HTTPTracingProvider(),
    ]
    context = {
        Config: config,
        DbConfig: config.db,
        WebAuthUserIdProviderConfig: config.web_auth_user_id_provider,
        TracingConfig: config.tracing,
        S3Config: config.s3,
        SuperuserConfig: config.superuser,
        SentryConfig: config.sentry,
    }
    container = make_async_container(*providers, context=context, validation_settings=STRICT_VALIDATION)
    return container
