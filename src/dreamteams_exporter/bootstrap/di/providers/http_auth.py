from dishka import Provider, Scope, WithParents, provide

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.broker.publisher import NatsJobEventBus
from dreamteams_exporter.adapters.http.applications_gateway import HttpApplicationsGateway
from dreamteams_exporter.adapters.idp.http_idp import HttpIdProvider
from dreamteams_exporter.application.common.event_bus import JobEventBus


class HttpAuthProvider(Provider):
    """Binds request-scoped types used by the HTTP entry point: IdProvider, AuthUserId, and auth-bearing gateways."""

    id_provider = provide(WithParents[HttpIdProvider], scope=Scope.REQUEST)
    applications_gateway = provide(WithParents[HttpApplicationsGateway], scope=Scope.REQUEST)
    event_bus = provide(NatsJobEventBus, scope=Scope.REQUEST, provides=JobEventBus)

    @provide(scope=Scope.REQUEST)
    def get_user_id(self, idp: HttpIdProvider) -> AuthUserId:
        """Exposes the caller id that the HTTP IdProvider extracted on construction."""
        return idp.user_id
