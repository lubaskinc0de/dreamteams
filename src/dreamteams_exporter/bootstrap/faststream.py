import asyncio

import sentry_sdk
from dishka_faststream import setup_dishka
from faststream import FastStream
from faststream.nats import NatsBroker

from dreamteams_common.logs import configure_structlog
from dreamteams_common.observability.setup import setup_observability
from dreamteams_exporter.bootstrap.config.loader import Config
from dreamteams_exporter.bootstrap.di.container import make_worker_container
from dreamteams_exporter.presentation.faststream.handlers import include_handlers


def create_worker(config: Config) -> FastStream:
    """Builds the FastStream worker with DI, OTel, and NATS subscribers wired in."""
    setup_observability(config.otel)
    if config.sentry.dsn:
        sentry_sdk.init(config.sentry.dsn)

    broker = NatsBroker(config.nats.url)
    include_handlers(broker)

    app = FastStream(broker)
    container = make_worker_container(config)
    setup_dishka(container=container, app=app, auto_inject=False)
    return app


async def _run_worker_async() -> None:
    config = Config.load()
    app = create_worker(config)
    try:
        await app.run()
    finally:
        pass


def run_worker() -> None:
    """Starts the FastStream NATS worker subscribed to the configured stream."""
    configure_structlog()
    asyncio.run(_run_worker_async())
