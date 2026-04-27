from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.competition_tag import CompetitionTagAlreadyExistsError
from dreamteams.application.manage_users.shared import ensure_admin
from dreamteams.entities.competition.tag import CompetitionTag, competition_tag_factory


class CompetitionTagInput(BaseModel):
    """Request body for creating a competition tag."""

    value: str = Field(min_length=1, max_length=100)


@interactor
class CreateCompetitionTag:
    """Interactor for creating a competition tag as an admin."""

    uow: UoW
    idp: IdProvider
    user_gateway: UserGateway
    competition_tag_gateway: CompetitionTagGateway

    async def execute(self, data: CompetitionTagInput) -> CompetitionTag:
        """Create a competition tag."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        existing = await self.competition_tag_gateway.get_by_value(data.value)
        if existing is not None:
            raise CompetitionTagAlreadyExistsError

        tag = competition_tag_factory(data.value)
        self.uow.add(tag)
        await self.uow.commit()

        return tag
