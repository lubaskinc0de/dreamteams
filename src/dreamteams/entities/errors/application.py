from typing import ClassVar

from dreamteams.entities.errors import AppError, app_error


@app_error
class InvalidApplicationDataError(AppError):
    """Application data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_APPLICATION_DATA"


@app_error
class ApplicationAlreadyResolvedError(AppError):
    """Application is not in PENDING status."""

    code: ClassVar[str] = "APPLICATION_ALREADY_RESOLVED"
    message: str = "Application has already been resolved"
