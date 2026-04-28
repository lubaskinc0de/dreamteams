from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from dreamteams.adapters.sentry import SentryConfig
from dreamteams.bootstrap.config.loader import Config
from dreamteams.bootstrap.di.container import get_async_container
from dreamteams.presentation.fast_api import include_exception_handlers, include_routers
from dreamteams.presentation.fast_api.tracing import tracing_middleware
from dreamteams_common.logs import configure_structlog
from dreamteams_common.observability.setup import setup_observability

log_config = configure_structlog()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle DI container lifecycle during application startup and shutdown."""
    container: AsyncContainer = app.state.dishka_container
    sentry_config = await container.get(SentryConfig)

    if sentry_config.dsn:
        sentry_sdk.init(sentry_config.dsn)

    yield
    await container.close()


def create_app(config: Config) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    setup_observability(config.otel)

    app = FastAPI(
        lifespan=lifespan,
        root_path=config.api.root_path,
    )

    # OTel added first → outermost → creates span before tracing_middleware reads it
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="/internal/alive,/internal/ready",
    )
    app.middleware("http")(tracing_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
    )
    container = get_async_container(config)
    setup_dishka(container=container, app=app)

    include_routers(app)
    include_exception_handlers(app)

    return app


def app_factory() -> FastAPI:
    """Module-level zero-arg factory used by uvicorn workers (must be import-string-resolvable)."""
    return create_app(Config.load())


def run_api() -> None:
    """Start the FastAPI application server."""
    config = Config.load()
    uvicorn.run(
        "dreamteams.bootstrap.fast_api:app_factory",
        factory=True,
        port=config.server.port,
        host=config.server.host,
        workers=config.server.workers,
        log_config=log_config,
    )


if __name__ == "__main__":
    run_api()
