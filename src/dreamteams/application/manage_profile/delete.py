import structlog
from opentelemetry import trace

from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class DeleteProfile:
    """Interactor for deleting user profile."""

    uow: UoW
    idp: IdProvider

    async def execute(self) -> None:
        """Delete user profile."""
        with _tracer.start_as_current_span("interactor.delete_profile"):
            user = await self.idp.get_user()
            logger.debug("Removing user profile", user_id=user.id)

            await self.uow.delete(user)
            await self.uow.commit()
