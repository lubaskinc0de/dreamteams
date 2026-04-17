import structlog
from opentelemetry import trace
from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.manage_my_applications.read import ApplicationModel
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")

PAGE_SIZE = 20


class ApplicationsList(BaseModel):
    """Paginated list of applications for a competition."""

    items: list[ApplicationModel]
    total: int
    page: int


@interactor
class ListApplicationsByCompetition:
    """Interactor for listing all applications submitted to a competition."""

    idp: IdProvider
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway

    async def execute(
        self,
        competition_id: CompetitionId,
        page: int = Field(ge=1, default=1),
    ) -> ApplicationsList:
        """List all applications for a competition; only the owning organizer may do this."""
        with _tracer.start_as_current_span("interactor.list_applications"):
            user = await self.idp.get_user()
            logger.debug(
                "Listing applications by competition",
                competition_id=competition_id,
                user_id=user.id,
                page=page,
            )

            competition = await self.competition_gateway.get(competition_id)
            if competition is None:
                logger.warning("Competition not found", competition_id=competition_id, user_id=user.id)
                raise CompetitionNotFoundError

            if not competition.can_read(user):
                logger.warning("Access denied to list applications", competition_id=competition_id, user_id=user.id)
                raise AccessDeniedError(
                    message="Only the organizer who owns this competition can list its applications",
                )

            applications, total = await self.application_gateway.list_by_competition(
                competition_id,
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
