from uuid import uuid4

import structlog
from pydantic import BaseModel

from posutochnik.application.common.auth_provider import AuthProvider
from posutochnik.application.common.interactor import interactor
from posutochnik.application.common.logger import Logger
from posutochnik.application.common.uow import UoW
from posutochnik.entities.common.identifiers import UserId
from posutochnik.entities.user import create_new_user

logger: Logger = structlog.get_logger(__name__)


class CreatedUser(BaseModel):
    """Response model containing the info about newly created user."""

    id: UserId


@interactor
class CreateUser:
    """Interactor for creating a new user entity."""

    uow: UoW
    auth_provider: AuthProvider

    async def execute(self) -> CreatedUser:
        """Creates a new user with a generated ID."""
        logger.debug("Creating new user")
        user_id = uuid4()
        logger.debug("Generated new user id", user_id=user_id)
        user = create_new_user(user_id)

        self.uow.add(user)
        await self.uow.flush([user])
        await self.auth_provider.setup_auth(user)
        await self.uow.commit()

        logger.info("User created", user=user)
        return CreatedUser(
            id=user_id,
        )
