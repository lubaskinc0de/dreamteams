from dataclasses import dataclass

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import User

type AuthUserId = str


@dataclass
class AuthUser:
    """Entity representing the link between an external authentication system user and an application user."""

    auth_user_id: AuthUserId
    user_id: UserId
    user: User
