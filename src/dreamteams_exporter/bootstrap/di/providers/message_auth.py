from dishka import Provider, Scope, provide

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.applications_gateway import HttpApplicationsGateway
from dreamteams_exporter.adapters.idp.message_idp import MessageIdProvider
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.application.common.idp import IdProvider


class MessageAuthProvider(Provider):
    """Binds request-scoped types used by the FastStream worker entry point."""

    id_provider = provide(MessageIdProvider, scope=Scope.REQUEST, provides=IdProvider)
    applications_gateway = provide(HttpApplicationsGateway, scope=Scope.REQUEST, provides=ApplicationsGateway)

    @provide(scope=Scope.REQUEST)
    def get_user_id(self, idp: MessageIdProvider) -> AuthUserId:
        """Exposes the caller id that the worker IdProvider extracted on construction."""
        return idp.user_id
