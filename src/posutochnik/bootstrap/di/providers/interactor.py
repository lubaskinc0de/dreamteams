from dishka import BaseScope, Provider, Scope, provide, provide_all

from posutochnik.application.register.landlord import RegisterLandlord
from posutochnik.application.register.shared.user_factory import UserFactory


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        RegisterLandlord,
    )
    user_factory = provide(UserFactory)
