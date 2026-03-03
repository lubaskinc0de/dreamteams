from dishka import BaseScope, Provider, Scope, provide, provide_all

from dreamteams.application.manage_competitions import (
    DeleteCompetition,
    ListCompetitions,
    ReadCompetition,
    UpdateCompetition,
)
from dreamteams.application.manage_invites import IssueInvite, ListInvites, ReadInvite, RevokeInvite
from dreamteams.application.manage_profile import ReadProfile
from dreamteams.application.manage_profile.attach_avatar import AttachAvatar
from dreamteams.application.manage_profile.delete import DeleteProfile
from dreamteams.application.manage_profile.detach_avatar import DetachAvatar
from dreamteams.application.preview_competition.list import PreviewCompetitions
from dreamteams.application.publish_competition import CreateCompetition
from dreamteams.application.register.register_organizer import RegisterOrganizer
from dreamteams.application.register.register_superuser import RegisterSuperuser
from dreamteams.application.register.shared.user_factory import UserFactory


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        RegisterOrganizer,
        RegisterSuperuser,
        ReadProfile,
        CreateCompetition,
        ListCompetitions,
        ReadCompetition,
        DeleteCompetition,
        UpdateCompetition,
        AttachAvatar,
        DetachAvatar,
        PreviewCompetitions,
        DeleteProfile,
        IssueInvite,
        ListInvites,
        ReadInvite,
        RevokeInvite,
    )
    user_factory = provide(UserFactory)
