from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class InvalidCompetitionDataError(AppError):
    """Competition data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_COMPETITION_DATA"


@app_error
class CompetitionNotFoundError(AppError):
    """Competition not found."""

    code: ClassVar[str] = "COMPETITION_NOT_FOUND"
    message: str = "Competition not found"
