from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class OrganizerAlreadyExistsError(AppError):
    """The error occurs when an organizer with the same phone number or email already exists."""

    code: ClassVar[str] = "ORGANIZER_ALREADY_EXISTS"
    message: str = "Organizer with this phone number or email already exists"
