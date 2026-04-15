from typing import ClassVar

from dreamteams.entities.errors import AppError, app_error


@app_error
class InvalidApplicationDataError(AppError):
    """Application data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_APPLICATION_DATA"


@app_error
class ApplicationAlreadyResolvedError(AppError):
    """Application is not in PENDING status."""

    code: ClassVar[str] = "APPLICATION_ALREADY_RESOLVED"
    message: str = "Application has already been resolved"


@app_error
class CompetitionNotActiveError(AppError):
    """Competition is archived or its registration window is not currently open."""

    code: ClassVar[str] = "COMPETITION_NOT_ACTIVE"
    message: str = "Competition is not accepting applications"


@app_error
class ParticipantTypeMismatchError(AppError):
    """Participant type does not match the competition's required participant type."""

    code: ClassVar[str] = "PARTICIPANT_TYPE_MISMATCH"
    message: str = "Your participant type does not match the competition requirements"


@app_error
class ParticipantLimitsExceededError(AppError):
    """Competition has reached its maximum accepted participant count."""

    code: ClassVar[str] = "PARTICIPANT_LIMITS_EXCEEDED"
    message: str = "Competition has reached its participant limit"
