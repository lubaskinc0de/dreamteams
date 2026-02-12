from typing import ClassVar

from dreamteams.entities.errors import AppError, app_error


@app_error
class InvalidParticipantDataError(AppError):
    """Participant contact data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_PARTICIPANT_DATA"
