from dreamteams.application.block_user.shared import ensure_admin
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.errors.competition_tag import CompetitionTagNotFoundError
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.competition.tag import CompetitionTag


@interactor
class ReadCompetitionTag:
    """Interactor for reading a competition tag as an admin."""

    idp: IdProvider
    user_gateway: UserGateway
    competition_tag_gateway: CompetitionTagGateway

    async def execute(self, tag_id: CompetitionTagId) -> CompetitionTag:
        """Read a competition tag."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        tag = await self.competition_tag_gateway.get(tag_id)
        if tag is None:
            raise CompetitionTagNotFoundError

        return tag
