from posutochnik.entities.base import model
from posutochnik.entities.common.identifiers import UserId
from posutochnik.entities.user import User

type AuthUserId = str


@model
class AuthUser:
    """Entity representing the link between an external authentication system user and an application user."""

    auth_user_id: AuthUserId
    user_id: UserId
    user: User
