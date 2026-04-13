from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class ApplicationFormNotFoundError(AppError):
    """No ApplicationForm exists for the given competition."""

    code: ClassVar[str] = "APPLICATION_FORM_NOT_FOUND"
    message: str = "Application form not found"


@app_error
class ApplicationFormAlreadyExistsError(AppError):
    """An ApplicationForm already exists for the given competition."""

    code: ClassVar[str] = "APPLICATION_FORM_ALREADY_EXISTS"
    message: str = "Application form already exists for this competition"
