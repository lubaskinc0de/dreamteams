from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class InvalidJobStatusError(AppError):
    """Raised when a JobStatus value object is constructed with an inconsistent reason field."""

    code: ClassVar[str] = "INVALID_JOB_STATUS"
    message: str = "Invalid job status"


@app_error
class InvalidJobStatusTransitionError(AppError):
    """Raised when mark_success/mark_failed is called on a job that is not in a pending state."""

    code: ClassVar[str] = "INVALID_JOB_STATUS_TRANSITION"
    message: str = "Invalid job status transition"
