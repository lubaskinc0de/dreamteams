from .auth_user import auth_user_table
from .base import mapper_registry
from .competition import competition_table
from .organizer import organizer_table
from .user import user_table

__all__ = [
    "auth_user_table",
    "competition_table",
    "mapper_registry",
    "organizer_table",
    "user_table",
]
