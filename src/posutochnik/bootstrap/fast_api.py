from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from posutochnik.bootstrap.config.loader import Config
from posutochnik.bootstrap.di.container import get_async_container
from posutochnik.bootstrap.logs import configure_structlog
from posutochnik.presentation.fast_api import include_exception_handlers, include_routers
from posutochnik.presentation.fast_api.tracing import tracing_middleware

log_config = configure_structlog()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan context manager that handles DI container lifecycle during application startup and shutdown."""
    yield
    await app.state.dishka_container.close()


def create_app(config: Config) -> FastAPI:
    """Creates and configures the FastAPI application instance with routers, error handlers, and DI container."""
    app = FastAPI(
        lifespan=lifespan,
        root_path=config.api.root_path,
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


def run_api() -> None:
    """Starts the FastAPI application server using uvicorn on the configured host and port."""
    config = Config.load()
    uvicorn.run(
        create_app(config),
        port=config.server.server_port,
        host=config.server.server_host,
        log_config=log_config,
    )


if __name__ == "__main__":
    run_api()
