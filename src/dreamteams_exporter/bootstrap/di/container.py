from dishka import STRICT_VALIDATION, AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider
from dishka_faststream import FastStreamProvider

from dreamteams_common.observability.config import OTelConfig
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.db.config import DbConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.bootstrap.config.loader import Config
from dreamteams_exporter.bootstrap.config.sentry import SentryConfig
from dreamteams_exporter.bootstrap.config.server import ServerConfig
from dreamteams_exporter.bootstrap.di.providers.adapter import AdapterProvider
from dreamteams_exporter.bootstrap.di.providers.config import ConfigProvider
from dreamteams_exporter.bootstrap.di.providers.http_auth import HttpAuthProvider
from dreamteams_exporter.bootstrap.di.providers.interactor import InteractorProvider
from dreamteams_exporter.bootstrap.di.providers.message_auth import MessageAuthProvider


def _context(config: Config) -> dict[type, object]:
    return {
        Config: config,
        DbConfig: config.db,
        CacheConfig: config.cache,
        NatsConfig: config.nats,
        S3Config: config.s3,
        DreamteamsApiConfig: config.dreamteams_api,
        ServerConfig: config.server,
        OTelConfig: config.otel,
        SentryConfig: config.sentry,
    }


def make_http_container(config: Config) -> AsyncContainer:
    """Builds the DI container used by the internal FastAPI app."""
    return make_async_container(
        ConfigProvider(),
        FastapiProvider(),
        AdapterProvider(),
        HttpAuthProvider(),
        InteractorProvider(),
        context=_context(config),
        validation_settings=STRICT_VALIDATION,
    )


def make_worker_container(config: Config) -> AsyncContainer:
    """Builds the DI container used by the FastStream NATS worker."""
    return make_async_container(
        ConfigProvider(),
        FastStreamProvider(),
        AdapterProvider(),
        MessageAuthProvider(),
        InteractorProvider(),
        context=_context(config),
        validation_settings=STRICT_VALIDATION,
    )
