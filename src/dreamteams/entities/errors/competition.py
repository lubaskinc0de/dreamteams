from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class InvalidCompetitionDataError(AppError):
    """Competition data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_COMPETITION_DATA"
