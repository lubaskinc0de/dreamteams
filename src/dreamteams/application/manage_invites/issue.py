from uuid import uuid4

import structlog
from pydantic import BaseModel

from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import OrganizerInviteId
from dreamteams.entities.organizer_invite import organizer_invite_factory

logger: Logger = structlog.get_logger(__name__)


class IssueInviteForm(BaseModel):
    """Form for issuing a new organizer invite."""

    display_name: str | None = None


class InviteIssued(BaseModel):
    """Response model after successfully issuing an invite."""

    invite_id: OrganizerInviteId
    code: str


@interactor
class IssueInvite:
    """Interactor for issuing a new organizer invite code. Admin only."""

    uow: UoW
    idp: IdProvider

    async def execute(self, data: IssueInviteForm) -> InviteIssued:
        """Create a new organizer invite with a unique code."""
        user = await self.idp.get_user()
        logger.debug("Issuing invite", user_id=user.id)

        invite_id = uuid4()
        invite = organizer_invite_factory(
            invite_id=invite_id,
            display_name=data.display_name,
            user=user,
        )

        self.uow.add(invite)
        await self.uow.commit()

        logger.info("Invite issued", invite_id=invite_id, user_id=user.id)
        return InviteIssued(invite_id=invite_id, code=invite.code)
