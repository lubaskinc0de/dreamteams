from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class InvalidApplicationFormDataError(AppError):
    """Application form definition is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_APPLICATION_FORM_DATA"
