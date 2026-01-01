from dishka import BaseScope, Provider, Scope, provide, provide_all

from dreamteams.application.create_competition.interactor import CreateCompetition
from dreamteams.application.delete_competition.interactor import DeleteCompetition
from dreamteams.application.read_competition.interactor import ReadCompetition
from dreamteams.application.register.organizer import RegisterOrganizer
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.application.update_competition.interactor import UpdateCompetition
from dreamteams.application.view_profile.interactor import ViewProfile


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        RegisterOrganizer,
        ViewProfile,
        CreateCompetition,
        ReadCompetition,
        DeleteCompetition,
        UpdateCompetition,
    )
    user_factory = provide(UserFactory)
