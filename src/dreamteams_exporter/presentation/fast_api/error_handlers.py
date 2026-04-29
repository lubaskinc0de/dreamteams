import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from dreamteams_common.errors import AppError
from dreamteams_common.logger import Logger
from dreamteams_exporter.adapters.errors.http.response import (
    ErrorResponse,
    InternalServerError,
    ValidationError,
)
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.application.errors.rate_limit import RateLimitExceededError
from dreamteams_exporter.entities.errors.job import (
    InvalidJobStatusError,
    InvalidJobStatusTransitionError,
)
from dreamteams_exporter.entities.errors.user import InvalidRoleError

SERVER_ERROR = 500
logger: Logger = structlog.get_logger(__name__)

error_to_http_status: dict[type[AppError], int] = {
    ValidationError: 422,
    UnauthorizedError: 401,
    InvalidRoleError: 403,
    RateLimitExceededError: 429,
    JobNotFoundError: 404,
    InvalidJobStatusError: 422,
    InvalidJobStatusTransitionError: 409,
}


async def get_app_error_response(err: AppError) -> JSONResponse:
    """Converts an AppError into the standard JSON response with the mapped HTTP status."""
    http_status = error_to_http_status.get(type(err))
    if http_status is None:
        logger.critical(
            "AppError is missing status code mapping",
            error_type=err.__class__.__qualname__
            if not isinstance(err, InternalServerError)
            else err.orig_error.__class__.__qualname__,
        )
        http_status = SERVER_ERROR

    payload = ErrorResponse(code=err.code, message=err.message, meta=err.meta).model_dump(mode="json")

    if http_status < SERVER_ERROR:
        logger.info("Handled error", error_response=payload, exc_info=err)
    else:
        logger.error("Unexpected error", exc_info=err)

    return JSONResponse(status_code=http_status, content=payload)


async def app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Top-level exception hook: converts AppError subclasses into JSON, wraps anything else as InternalServerError."""
    span = trace.get_current_span()
    span.record_exception(exc)

    app_error = exc if isinstance(exc, AppError) else None
    if app_error is None:
        logger.exception("Handling unexpected internal server error", exc_info=exc)
        span.set_status(StatusCode.ERROR, str(exc))
        app_error = InternalServerError(orig_error=exc)
    return await get_app_error_response(app_error)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalises FastAPI ``RequestValidationError`` into our standard ValidationError envelope."""
    return await app_error_handler(
        request,
        ValidationError(details=jsonable_encoder({"detail": exc.errors(), "body": exc.body})),
    )


def include_exception_handlers(app: FastAPI) -> None:
    """Registers the exporter's AppError + validation handlers on the given FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, app_error_handler)
