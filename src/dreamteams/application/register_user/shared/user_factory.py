from uuid import uuid4

import structlog

from dreamteams.application.common.auth_provider import AuthProvider
from dreamteams.entities.user import User, user_factory
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

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
        user = user_factory(user_id)

        self.uow.add(user)
        await self.uow.flush([user])
        await self.auth_provider.setup_auth(user)

        logger.info("User created", user=user)
        return user
