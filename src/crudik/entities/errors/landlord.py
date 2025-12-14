from typing import ClassVar

from crudik.entities.errors.base import AppError, app_error


@app_error
class UserAlreadyLandlordError(AppError):
    """The error occurs when an attempt is made to create a landlord role for a user who is already a landlord."""

    code: ClassVar[str] = "USER_ALREADY_LANDLORD"
    message: str = "User already has landlord role"


@app_error
class LandlordUserIdMismatchError(AppError):
    """The error occurs when an attempt is made to attach a landlord to user B with a user id of user A."""

    code: ClassVar[str] = "LANDLORD_USER_ID_MISMATCH"
    message: str = "You're trying to attach a landlord of user A to user B"
