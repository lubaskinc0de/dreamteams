from dataclasses import dataclass
from typing import override

import aiohttp
from adaptix import ExtraSkip, Retort, name_mapping
from opentelemetry import trace

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.application.common.dto.application import ApplicationsPage
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.common.identifiers import CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.participant.entity import Participant


@dataclass(slots=True, frozen=True, kw_only=True)
class _ApplicationsListPayload:
    """Wire shape of main's ``ApplicationsList`` — only the fields we need to paginate."""

    items: list[Application]
    total: int
    page: int


_retort = Retort(
    recipe=[
        name_mapping(Application, extra_in=ExtraSkip()),
        name_mapping(Participant, extra_in=ExtraSkip()),
    ],
)
_tracer = trace.get_tracer(__name__)


class HttpApplicationsGateway(ApplicationsGateway):
    """Fetches paginated applications."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        config: DreamteamsApiConfig,
        user_id: AuthUserId,
    ) -> None:
        self._session = session
        self._config = config
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
        url = f"{self._config.base_url}/competitions/{competition_id}/applications/"
        headers = {self._config.auth_header_name: self._user_id}
        params: dict[str, str | int] = {
            "page": page,
            "page_size": page_size,
        }
        if status is not None:
            params["status"] = status.value

        with _tracer.start_as_current_span("dreamteams_exporter.main_api.list_applications") as span:
            span.set_attribute("dreamteams_exporter.main_api.route", "/competitions/{competition_id}/applications/")
            span.set_attribute("dreamteams_exporter.main_api.page", page)
            span.set_attribute("dreamteams_exporter.main_api.page_size", page_size)
            span.set_attribute("dreamteams_exporter.main_api.competition_id", str(competition_id))
            if status is not None:
                span.set_attribute("dreamteams_exporter.main_api.application_status", status.value)

            async with self._session.get(url, headers=headers, params=params) as response:
                span.set_attribute("http.response.status_code", response.status)
                response.raise_for_status()
                payload = await response.json()

            parsed = _retort.load(payload, _ApplicationsListPayload)
            span.set_attribute("dreamteams_exporter.main_api.items_count", len(parsed.items))
            span.set_attribute("dreamteams_exporter.main_api.total_count", parsed.total)
            return ApplicationsPage(
                items=parsed.items,
                page=parsed.page,
                page_size=page_size,
                total=parsed.total,
            )
