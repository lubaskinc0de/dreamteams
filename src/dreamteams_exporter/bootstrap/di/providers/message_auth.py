from dishka import Provider, Scope, WithParents, provide

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.applications_gateway import HttpApplicationsGateway
from dreamteams_exporter.adapters.idp.message_idp import MessageIdProvider


class MessageAuthProvider(Provider):
    """Binds request-scoped types used by the FastStream worker entry point."""

    id_provider = provide(WithParents[MessageIdProvider], scope=Scope.REQUEST)
    applications_gateway = provide(WithParents[HttpApplicationsGateway], scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    def get_user_id(self, idp: MessageIdProvider) -> AuthUserId:
        """Exposes the caller id that the worker IdProvider extracted on construction."""
        return idp.user_id
