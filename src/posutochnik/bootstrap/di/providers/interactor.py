from dishka import BaseScope, Provider, Scope, provide, provide_all

from posutochnik.application.register.landlord import RegisterLandlord
from posutochnik.application.register.shared.user_factory import UserFactory
from posutochnik.application.view_profile.interactor import ViewProfile


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        RegisterLandlord,
        ViewProfile,
    )
    user_factory = provide(UserFactory)
