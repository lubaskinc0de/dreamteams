from dataclasses import dataclass
from typing import override

import aiohttp
from adaptix import ExtraSkip, Retort, name_mapping

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
        status: ApplicationStatus,
        page: int,
        page_size: int,
    ) -> ApplicationsPage:
        """Fetches one page of applications for the given competition + status."""
        url = f"{self._config.base_url}/competitions/{competition_id}/applications/"
        headers = {self._config.auth_header_name: self._user_id}
        params: dict[str, str | int] = {
            "page": page,
            "page_size": page_size,
            "status": status.value,
        }

        async with self._session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            payload = await response.json()

        parsed = _retort.load(payload, _ApplicationsListPayload)
        return ApplicationsPage(
            items=parsed.items,
            page=parsed.page,
            page_size=page_size,
            total=parsed.total,
        )
