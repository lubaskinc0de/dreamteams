from dreamteams.application.block_user.shared import ensure_admin
from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import CompetitionTagDeleted
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.competition_tag import CompetitionTagNotFoundError
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams_common.interactor import interactor
from dreamteams_common.uow import UoW


@interactor
class DeleteCompetitionTag:
    """Interactor for deleting a competition tag as an admin."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    competition_tag_gateway: CompetitionTagGateway
    event_bus: EventBus

    async def execute(self, tag_id: CompetitionTagId) -> None:
        """Delete a competition tag."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        tag = await self.competition_tag_gateway.get(tag_id)
        if tag is None:
            raise CompetitionTagNotFoundError

        await self.uow.delete(tag)
        await self.uow.commit()
        await self.event_bus.publish(CompetitionTagDeleted(tag_id=tag_id))
