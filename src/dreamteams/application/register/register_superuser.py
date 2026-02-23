import asyncio
from dataclasses import dataclass

import structlog
from pydantic import BaseModel

from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.password_hasher import PasswordHasher
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.user import InvalidSuperuserPasswordError
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.entities.common.identifiers import UserId

logger: Logger = structlog.get_logger(__name__)


@dataclass(slots=True, frozen=True)
class SuperuserConfig:
    """Configuration for superuser registration."""

    password_hash: str


class SuperuserForm(BaseModel):
    """Form for registering as superuser."""

    password: str


class CreatedSuperuser(BaseModel):
    """Response model for a newly created superuser."""

    user_id: UserId


@interactor
class RegisterSuperuser:
    """Interactor for registering a new superuser (admin user)."""

    uow: UoW
    user_factory: UserFactory
    password_hasher: PasswordHasher
    superuser_config: SuperuserConfig

    async def execute(self, data: SuperuserForm) -> CreatedSuperuser:
        """Create a new user with is_admin=True if the password matches the configured hash."""
        logger.debug("Attempting superuser registration")

        matches = await asyncio.to_thread(
            self.password_hasher.verify,
            self.superuser_config.password_hash,
            data.password,
        )
        if not matches:
            logger.warning("Invalid superuser password supplied")
            raise InvalidSuperuserPasswordError

        user = await self.user_factory.create_user()
        user.is_admin = True

        await self.uow.commit()

        logger.info("Superuser created", user_id=user.id)
        return CreatedSuperuser(user_id=user.id)
