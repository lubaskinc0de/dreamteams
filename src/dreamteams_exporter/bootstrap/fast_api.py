from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from dreamteams_common.logs import configure_structlog
from dreamteams_common.observability.setup import setup_observability
from dreamteams_exporter.bootstrap.config.loader import Config
from dreamteams_exporter.bootstrap.di.container import make_http_container
from dreamteams_exporter.presentation.fast_api.error_handlers import include_exception_handlers
from dreamteams_exporter.presentation.fast_api.routers import include_routers


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    container: AsyncContainer = app.state.dishka_container
    yield
    await container.close()


def create_app(config: Config) -> FastAPI:
    """Builds the exporter's internal FastAPI app with DI, OTel, and error handlers wired in."""
    setup_observability(config.otel)
    if config.sentry.dsn is not None:
        sentry_sdk.init(config.sentry.dsn)

    app = FastAPI(lifespan=_lifespan)

    FastAPIInstrumentor.instrument_app(app)
    AioHttpClientInstrumentor().instrument()

    container = make_http_container(config)
    setup_dishka(container=container, app=app)

    include_routers(app)
    include_exception_handlers(app)
    return app


def app_factory() -> FastAPI:
    """Module-level zero-arg factory used by ``uvicorn`` when spawning workers."""
    return create_app(Config.load())


def run_api() -> None:
    """Starts the internal FastAPI server, honouring binding parameters from the TOML config."""
    log_config = configure_structlog()
    config = Config.load()
    uvicorn.run(
        "dreamteams_exporter.bootstrap.fast_api:app_factory",
        factory=True,
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        log_config=log_config,
    )
