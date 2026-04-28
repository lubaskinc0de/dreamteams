import asyncio
from dataclasses import dataclass

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.password_hasher import PasswordHasher
from dreamteams.application.errors.user import InvalidSuperuserPasswordError
from dreamteams.application.register_user.shared.user_factory import UserFactory
from dreamteams.entities.common.identifiers import UserId
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

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
    idp: IdProvider
    user_gateway: UserGateway
    user_factory: UserFactory
    password_hasher: PasswordHasher
    superuser_config: SuperuserConfig

    async def execute(self, data: SuperuserForm) -> CreatedSuperuser:
        """Promote the current user to admin, creating a new user if one does not exist yet."""
        logger.debug("Attempting superuser registration")

        matches = await asyncio.to_thread(
            self.password_hasher.verify,
            self.superuser_config.password_hash,
            data.password,
        )
        if not matches:
            logger.warning("Invalid superuser password supplied")
            raise InvalidSuperuserPasswordError

        user_id = await self.idp.get_user_id_or_none()
        user = await self.user_gateway.get(user_id) if user_id is not None else None
        if user is None:
            user = await self.user_factory.create_user()

        user.is_admin = True

        await self.uow.commit()

        logger.info("Superuser created", user_id=user.id)
        return CreatedSuperuser(user_id=user.id)
