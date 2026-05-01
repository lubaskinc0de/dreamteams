import structlog
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from dreamteams.adapters.auth.errors.auth_user import AuthUserAlreadyExistsError
from dreamteams.adapters.auth.errors.base import UnauthorizedError
from dreamteams.adapters.db.gateway.competition import CompetitionBusyError
from dreamteams.adapters.errors.http.response import ErrorResponse, InternalServerError, ValidationError
from dreamteams.application.errors.application import ApplicationAlreadyExistsError, ApplicationNotFoundError
from dreamteams.application.errors.application_form import (
    ApplicationFormAlreadyExistsError,
    ApplicationFormNotFoundError,
)
from dreamteams.application.errors.competition_tag import (
    CompetitionTagAlreadyExistsError,
    CompetitionTagNotFoundError,
)
from dreamteams.application.errors.invite import InviteNotFoundError
from dreamteams.application.errors.organizer import OrganizerAlreadyExistsError, OrganizerNotFoundError
from dreamteams.application.errors.participant import ParticipantNotFoundError
from dreamteams.application.errors.user import InvalidSuperuserPasswordError, UserBlockedError, UserNotFoundError
from dreamteams.entities.errors.application import (
    ApplicationAlreadyResolvedError,
    CompetitionNotActiveError,
    InvalidApplicationDataError,
    ParticipantLimitsExceededError,
    ParticipantTypeMismatchError,
)
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError, InvalidCompetitionDataError
from dreamteams.entities.errors.invite import InviteAlreadyRevokedError, InviteAlreadyUsedError, InviteRevokedError
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.presentation.fast_api.errors import InvalidAvatarError
from dreamteams_common.errors import AppError
from dreamteams_common.logger import Logger

SERVER_ERROR = 500
logger: Logger = structlog.get_logger(__name__)


error_to_http_status: dict[type[AppError], int] = {
    ValidationError: 422,
    UnauthorizedError: 401,
    AuthUserAlreadyExistsError: 409,
    UserNotFoundError: 404,
    UserBlockedError: 403,
    AccessDeniedError: 403,
    OrganizerAlreadyExistsError: 409,
    InvalidCompetitionDataError: 422,
    CompetitionNotFoundError: 404,
    InvalidAvatarError: 422,
    InviteNotFoundError: 404,
    InviteAlreadyRevokedError: 409,
    InviteAlreadyUsedError: 409,
    InviteRevokedError: 403,
    InvalidSuperuserPasswordError: 403,
    ApplicationFormNotFoundError: 404,
    ApplicationFormAlreadyExistsError: 409,
    InvalidApplicationFormDataError: 400,
    InvalidParticipantDataError: 400,
    ApplicationNotFoundError: 404,
    ApplicationAlreadyExistsError: 409,
    InvalidApplicationDataError: 400,
    ApplicationAlreadyResolvedError: 409,
    CompetitionNotActiveError: 409,
    ParticipantTypeMismatchError: 422,
    ParticipantLimitsExceededError: 409,
    OrganizerNotFoundError: 404,
    ParticipantNotFoundError: 404,
    CompetitionTagNotFoundError: 404,
    CompetitionTagAlreadyExistsError: 409,
    CompetitionBusyError: 429,
}


async def get_app_error_response(
    err: AppError,
) -> JSONResponse:
    """Converts an AppError to an appropriate HTTP JSON response with status code mapping."""
    try:
        http_status = error_to_http_status[type(err)]
    except KeyError:
        logger.critical(
            "AppError is missing status code mapping",
            error_type=err.__class__.__qualname__
            if not isinstance(err, InternalServerError)
            else err.orig_error.__class__.__qualname__,
        )
        http_status = 500

    error_response = ErrorResponse(
        code=err.code,
        message=err.message,
        meta=err.meta,
    ).model_dump(mode="json")

    if http_status < SERVER_ERROR:
        logger.info("Handled error", error_response=error_response, exc_info=err)
    else:
        logger.error("Unexpected error", exc_info=err)

    return JSONResponse(
        status_code=http_status,
        content=error_response,
    )


async def app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """FastAPI exception handler that converts AppError exceptions to JSON error responses."""
    span = trace.get_current_span()
    span.record_exception(exc)
    app_error = exc if isinstance(exc, AppError) else None
    if app_error is None:
        logger.exception("Handling unexpected internal server error", exc_info=exc)
        span.set_status(StatusCode.ERROR, str(exc))
        app_error = InternalServerError(orig_error=exc)
    return await get_app_error_response(app_error)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """FastAPI exception handler that converts RequestValidationError exceptions to JSON error responses."""
    return await app_error_handler(
        request,
        ValidationError(details=jsonable_encoder({"detail": exc.errors(), "body": exc.body})),
    )
