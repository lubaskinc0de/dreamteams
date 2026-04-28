from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class OrganizerAlreadyExistsError(AppError):
    """The error occurs when an organizer with the same phone number or email already exists."""

    code: ClassVar[str] = "ORGANIZER_ALREADY_EXISTS"
    message: str = "Organizer with this phone number or email already exists"


@app_error
class OrganizerNotFoundError(AppError):
    """The error occurs when an organizer is not found."""

    code: ClassVar[str] = "ORGANIZER_NOT_FOUND"
    message: str = "Organizer not found"
