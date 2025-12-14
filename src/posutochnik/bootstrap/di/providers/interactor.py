from dishka import BaseScope, Provider, Scope, provide_all

from posutochnik.application.read_user import ReadUser
from posutochnik.application.register.create_user import CreateUser


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        CreateUser,
        ReadUser,
    )
