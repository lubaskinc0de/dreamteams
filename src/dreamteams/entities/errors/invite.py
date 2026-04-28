from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class InviteAlreadyRevokedError(AppError):
    """Raised when attempting to revoke an invite that has already been revoked."""

    code: ClassVar[str] = "INVITE_ALREADY_REVOKED"
    message: str = "This invite has already been revoked"


@app_error
class InviteRevokedError(AppError):
    """Raised when attempting to use a revoked invite (e.g. during organizer registration)."""

    code: ClassVar[str] = "INVITE_REVOKED"
    message: str = "This invite has been revoked"


@app_error
class InviteAlreadyUsedError(AppError):
    """Raised when attempting to use or revoke an invite that has already been used."""

    code: ClassVar[str] = "INVITE_ALREADY_USED"
    message: str = "This invite has already been used"
