from uuid import uuid4

import structlog

from dreamteams.application.common.auth_provider import AuthProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.user import User, create_new_user

logger: Logger = structlog.get_logger(__name__)


@interactor
class UserFactory:
    """Factory for creating a new ``User`` entity for register process."""

    uow: UoW
    auth_provider: AuthProvider

    async def create_user(self) -> User:
        """Creates a new ``User`` with a generated ID (doesn't commit current transaction)."""
        logger.debug("Creating new user")
        user_id = uuid4()
        logger.debug("Generated new user id", user_id=user_id)
        user = create_new_user(user_id)

        self.uow.add(user)
        await self.uow.flush([user])
        await self.auth_provider.setup_auth(user)

        logger.info("User created", user=user)
        return user
