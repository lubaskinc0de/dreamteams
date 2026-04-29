from typing import override

from opentelemetry import trace

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.client import DreamTeamsApiClient
from dreamteams_exporter.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams_exporter.entities.application_form.entity import ApplicationForm
from dreamteams_exporter.entities.common.identifiers import CompetitionId

_tracer = trace.get_tracer(__name__)


class HttpApplicationFormGateway(ApplicationFormGateway):
    """Fetches a competition's application form definition from the main app."""

    def __init__(
        self,
        client: DreamTeamsApiClient,
        user_id: AuthUserId,
    ) -> None:
        self._client = client
        self._user_id = user_id

    @override
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Fetch application form structure for the given competition."""
        with _tracer.start_as_current_span("dreamteams_exporter.main_api.get_application_form") as span:
            span.set_attribute(
                "dreamteams_exporter.main_api.route",
                "/competitions/{competition_id}/application-form/",
            )
            span.set_attribute("dreamteams_exporter.main_api.competition_id", str(competition_id))

            response = await self._client.get_application_form(self._user_id, competition_id)
            form = response.content

            span.set_attribute("http.response.status_code", response.status)
            found = form is not None
            span.set_attribute("dreamteams_exporter.main_api.found", found)
            if form is not None:
                span.set_attribute("dreamteams_exporter.main_api.form_fields_count", len(form.fields))
            return form
