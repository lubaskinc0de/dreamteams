import structlog

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.organizer_invite import OrganizerInviteGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.invite import InviteNotFoundError
from dreamteams.application.manage_invites.list import InviteModel, _organizer_info
from dreamteams.entities.common.identifiers import OrganizerInviteId

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadInvite:
    """Interactor for reading a single organizer invite by ID. Admin only."""

    idp: IdProvider
    avatar_storage: AvatarStorage
    organizer_invite_gateway: OrganizerInviteGateway

    async def execute(self, invite_id: OrganizerInviteId) -> InviteModel:
        """Return the invite belonging to the current admin or raise an error."""
        user = await self.idp.get_user()

        logger.debug("Reading invite", invite_id=invite_id, user_id=user.id)
        invite = await self.organizer_invite_gateway.get_by_id(invite_id)
        if invite is None:
            raise InviteNotFoundError

        invite.ensure_can_read(user)

        return InviteModel(
            id=invite.id,
            code=invite.code,
            display_name=invite.display_name,
            created_by=invite.created_by,
            is_revoked=invite.is_revoked,
            is_used=invite.is_used,
            used_by=_organizer_info(invite.used_by, self.avatar_storage) if invite.used_by else None,
            created_at=invite.created_at,
        )
