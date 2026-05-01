import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.application import MyApplicationModel
from dreamteams.application.common.gateway.application import ApplicationGateway, ApplicationSortBy
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.input_limits import MAX_PAGE
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)
PAGE_SIZE = 20


class ListMyApplicationsInput(BaseModel):
    """Input parameters for listing the current participant's applications."""

    page: int = Field(ge=1, le=MAX_PAGE, default=1)
    sort_by: ApplicationSortBy = ApplicationSortBy.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    status: ApplicationStatus | None = None


class ApplicationsList(BaseModel):
    """Paginated list of applications."""

    items: list[MyApplicationModel]
    total: int
    page: int


@interactor
class ListMyApplications:
    """Interactor for listing all applications submitted by the current participant."""

    idp: IdProvider
    participant_gateway: ParticipantGateway
    application_gateway: ApplicationGateway

    async def execute(self, input_data: ListMyApplicationsInput) -> ApplicationsList:
        """List all applications submitted by the current participant."""
        user_id = await self.idp.get_user_id()
        participant = await self.participant_gateway.get_by_user_id(user_id)
        logger.debug(
            "Listing own applications",
            user_id=user_id,
            page=input_data.page,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            status=input_data.status,
        )

        if participant is None:
            logger.warning("User has no participant profile", user_id=user_id)
            raise AccessDeniedError(message="Only participants can list their applications")

        items, total = await self.application_gateway.list_by_participant_with_competition(
            participant.id,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            status=input_data.status,
        )

        return ApplicationsList(items=items, total=total, page=input_data.page)
