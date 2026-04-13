import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.manage_my_applications.read import ApplicationModel
from dreamteams.entities.errors.base import AccessDeniedError

logger: Logger = structlog.get_logger(__name__)

PAGE_SIZE = 20


class ApplicationsList(BaseModel):
    """Paginated list of applications."""

    items: list[ApplicationModel]
    total: int
    page: int


@interactor
class ListMyApplications:
    """Interactor for listing all applications submitted by the current participant."""

    idp: IdProvider
    application_gateway: ApplicationGateway

    async def execute(self, page: int = Field(ge=1, default=1)) -> ApplicationsList:
        """List all applications submitted by the current participant."""
        user = await self.idp.get_user()
        logger.debug("Listing own applications", user_id=user.id, page=page)

        if user.participant is None:
            logger.warning("User has no participant profile", user_id=user.id)
            raise AccessDeniedError(message="Only participants can list their applications")

        applications, total = await self.application_gateway.list_by_participant(
            user.participant.id,
            page=page,
            page_size=PAGE_SIZE,
        )

        items = [
            ApplicationModel(
                id=app.id,
                participant_id=app.participant_id,
                competition_id=app.competition_id,
                domains=app.domains,
                status=app.status,
                created_at=app.created_at,
                form_data=app.form_data,
            )
            for app in applications
        ]

        return ApplicationsList(items=items, total=total, page=page)
