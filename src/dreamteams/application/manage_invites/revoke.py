import structlog
from opentelemetry import trace

from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.invite import InviteNotFoundError
from dreamteams.entities.common.identifiers import OrganizerInviteId

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class RevokeInvite:
    """Interactor for revoking an organizer invite. Admin only, creator only."""

    uow: UoW
    idp: IdProvider
    organizer_invite_gateway: OrganizerInviteGateway

    async def execute(self, invite_id: OrganizerInviteId) -> None:
        """Revoke an existing invite by its ID."""
        with _tracer.start_as_current_span("interactor.revoke_invite"):
            user = await self.idp.get_user()
            logger.debug("Revoking invite", invite_id=invite_id, user_id=user.id)

            invite = await self.organizer_invite_gateway.get_by_id(invite_id)
            if invite is None:
                logger.warning("Invite not found", invite_id=invite_id)
                raise InviteNotFoundError

            invite.revoke(user)
            self.uow.add(invite)
            await self.uow.commit()

            logger.info("Invite revoked", invite_id=invite_id, user_id=user.id)
