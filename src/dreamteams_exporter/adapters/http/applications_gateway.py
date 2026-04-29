from typing import override

from opentelemetry import trace

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.client import DreamTeamsApiClient
from dreamteams_exporter.application.common.dto.application import ApplicationsPage
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.entities.common.identifiers import CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus

_tracer = trace.get_tracer(__name__)


class HttpApplicationsGateway(ApplicationsGateway):
    """Fetches paginated applications."""

    def __init__(
        self,
        client: DreamTeamsApiClient,
        user_id: AuthUserId,
    ) -> None:
        self._client = client
        self._user_id = user_id

    @override
    async def list(
        self,
        *,
        competition_id: CompetitionId,
        status: ApplicationStatus | None,
        page: int,
        page_size: int,
    ) -> ApplicationsPage:
        """Fetches one page of applications for the given competition + optional status."""
        with _tracer.start_as_current_span("dreamteams_exporter.main_api.list_applications") as span:
            span.set_attribute("dreamteams_exporter.main_api.route", "/competitions/{competition_id}/applications/")
            span.set_attribute("dreamteams_exporter.main_api.page", page)
            span.set_attribute("dreamteams_exporter.main_api.page_size", page_size)
            span.set_attribute("dreamteams_exporter.main_api.competition_id", str(competition_id))
            if status is not None:
                span.set_attribute("dreamteams_exporter.main_api.application_status", status.value)

            response = await self._client.list_applications(
                self._user_id,
                competition_id=competition_id,
                status=status,
                page=page,
                page_size=page_size,
            )
            applications_page = response.content

            span.set_attribute("http.response.status_code", response.status)
            span.set_attribute("dreamteams_exporter.main_api.items_count", len(applications_page.items))
            span.set_attribute("dreamteams_exporter.main_api.total_count", applications_page.total)
            return applications_page
