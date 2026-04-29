from opentelemetry import trace

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.client import DreamTeamsApiClient
from dreamteams_exporter.entities.user import User

_tracer = trace.get_tracer(__name__)


class HttpUserGateway:
    """
    Adapter-internal helper that fetches the current User from main's ``GET /users/me``.

    Used by both ``HttpIdProvider`` and ``MessageIdProvider``. Not exposed as an application-layer
    protocol — the application layer only knows ``IdProvider``.
    """

    def __init__(self, client: DreamTeamsApiClient) -> None:
        self._client = client

    async def get_me(self, user_id: AuthUserId) -> User:
        """Issues ``GET {base}/users/me`` with the caller's ``X-Auth-User`` header forwarded verbatim."""
        with _tracer.start_as_current_span("dreamteams_exporter.main_api.get_me") as span:
            span.set_attribute("dreamteams_exporter.main_api.route", "/users/me")

            response = await self._client.get_me(user_id)
            user = response.content

            span.set_attribute("http.response.status_code", response.status)
            span.set_attribute("dreamteams_exporter.main_api.user_id", str(user.user_id))
            span.set_attribute("dreamteams_exporter.main_api.has_organizer", user.organizer_id is not None)
            span.set_attribute("dreamteams_exporter.main_api.has_participant", user.participant_id is not None)
            return user
