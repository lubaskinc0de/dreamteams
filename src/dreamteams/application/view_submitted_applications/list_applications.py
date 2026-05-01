import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.application import ApplicationModel
from dreamteams.application.common.gateway.application import ApplicationGateway, ApplicationSortBy
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.input_limits import MAX_PAGE
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)
PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class ListApplicationsByCompetitionInput(BaseModel):
    """Input parameters for listing applications of a competition."""

    page: int = Field(ge=1, le=MAX_PAGE, default=1)
    page_size: int = Field(ge=1, le=MAX_PAGE_SIZE, default=PAGE_SIZE)
    sort_by: ApplicationSortBy = ApplicationSortBy.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    status: ApplicationStatus | None = None


class ApplicationsList(BaseModel):
    """Paginated list of applications for a competition."""

    items: list[ApplicationModel]
    total: int
    page: int


@interactor
class ListApplicationsByCompetition:
    """Interactor for listing all applications submitted to a competition."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway

    async def execute(
        self,
        competition_id: CompetitionId,
        input_data: ListApplicationsByCompetitionInput,
    ) -> ApplicationsList:
        """List applications for a competition; only the owning organizer may do this."""
        user_id = await self.idp.get_user_id()
        logger.debug(
            "Listing applications by competition",
            competition_id=competition_id,
            user_id=user_id,
            page=input_data.page,
            page_size=input_data.page_size,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            status=input_data.status,
        )

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if not competition.is_owned_by(organizer):
            logger.warning("Access denied to list applications", competition_id=competition_id, user_id=user_id)
            raise AccessDeniedError(
                message="Only the organizer who owns this competition can list its applications",
            )

        items, total = await self.application_gateway.list_by_competition_with_participant(
            competition_id,
            competition.title,
            page=input_data.page,
            page_size=input_data.page_size,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            status=input_data.status,
        )

        return ApplicationsList(items=items, total=total, page=input_data.page)
