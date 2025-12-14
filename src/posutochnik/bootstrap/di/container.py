from dishka import STRICT_VALIDATION, AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from posutochnik.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from posutochnik.adapters.db.config import DbConfig
from posutochnik.adapters.tracing import TracingConfig
from posutochnik.bootstrap.config.loader import Config
from posutochnik.bootstrap.di.providers.adapter import AdapterProvider
from posutochnik.bootstrap.di.providers.config import ConfigProvider
from posutochnik.bootstrap.di.providers.interactor import InteractorProvider
from posutochnik.bootstrap.di.providers.tracing import HTTPTracingProvider


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
    }
    container = make_async_container(*providers, context=context, validation_settings=STRICT_VALIDATION)
    return container
