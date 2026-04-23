from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class JobNotFoundError(AppError):
    """Raised when the requested export job does not exist or is not visible to the caller."""

    code: ClassVar[str] = "EXPORT_JOB_NOT_FOUND"
    message: str = "Export job not found"
