from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class CompetitionTagNotFoundError(AppError):
    """Competition tag not found."""

    code: ClassVar[str] = "COMPETITION_TAG_NOT_FOUND"
    message: str = "Competition tag not found"


@app_error
class CompetitionTagAlreadyExistsError(AppError):
    """Competition tag with this value already exists."""

    code: ClassVar[str] = "COMPETITION_TAG_ALREADY_EXISTS"
    message: str = "Competition tag already exists"
