from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import User


def ensure_admin(user: User | None, user_id: UserId) -> None:
    """Ensure a loaded user exists and has admin privileges."""
    if user is None:
        raise UserNotFoundError(user_id=user_id)
    if not user.is_admin:
        raise AccessDeniedError(message="Only admins can manage users")
