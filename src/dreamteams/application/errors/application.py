from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class ApplicationNotFoundError(AppError):
    """No Application exists with the given ID."""

    code: ClassVar[str] = "APPLICATION_NOT_FOUND"
    message: str = "Application not found"


@app_error
class ApplicationAlreadyExistsError(AppError):
    """Participant already has an application for this competition."""

    code: ClassVar[str] = "APPLICATION_ALREADY_EXISTS"
    message: str = "Application already exists for this competition"
