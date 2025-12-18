from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from posutochnik.presentation.fast_api.error_handlers import app_error_handler, validation_error_handler
from posutochnik.presentation.fast_api.routers.landlords import router as landlords_router
from posutochnik.presentation.fast_api.routers.root import router as root_router


def include_routers(app: FastAPI) -> None:
    """Registers all API routers with the FastAPI application."""
    app.include_router(root_router)
    app.include_router(landlords_router)


def include_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for converting exceptions to HTTP error responses."""
    app.add_exception_handler(Exception, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]


__all__ = [
    "include_exception_handlers",
    "include_routers",
]
