from typing import Any, override

import aiohttp
from adaptix import ExtraSkip, Retort, name_mapping

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams_exporter.entities.application_form.entity import ApplicationForm, ApplicationFormField
from dreamteams_exporter.entities.common.identifiers import CompetitionId

_HTTP_NOT_FOUND = 404


_retort = Retort(
    recipe=[
        name_mapping(ApplicationForm, extra_in=ExtraSkip()),
        name_mapping(ApplicationFormField, extra_in=ExtraSkip()),
    ],
)


class HttpApplicationFormGateway(ApplicationFormGateway):
    """Fetches a competition's application form definition from the main app."""

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
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Fetch application form structure for the given competition."""
        url = f"{self._config.base_url}/competitions/{competition_id}/application-form/"
        headers = {self._config.auth_header_name: self._user_id}

        async with self._session.get(url, headers=headers) as response:
            if response.status == _HTTP_NOT_FOUND:
                payload: Any = await response.json()
                if isinstance(payload, dict) and payload.get("code") == "APPLICATION_FORM_NOT_FOUND":
                    return None
            response.raise_for_status()
            payload = await response.json()

        return _retort.load(payload, ApplicationForm)
