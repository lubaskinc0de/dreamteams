from dishka import BaseScope, Provider, Scope, provide, provide_all

from dreamteams.application.manage_application_form import (
    CreateApplicationForm,
    DeleteApplicationForm,
)
from dreamteams.application.manage_application_form import ReadApplicationForm as ReadApplicationFormAsOrganizer
from dreamteams.application.manage_applications import (
    AcceptApplication,
    ListApplicationsByCompetition,
    ReadApplication,
    RejectApplication,
)
from dreamteams.application.manage_competitions import (
    DeleteCompetition,
    ListCompetitions,
    UpdateCompetition,
)
from dreamteams.application.manage_competitions import ReadCompetition as ReadCompetitionAsOrganizer
from dreamteams.application.manage_invites import IssueInvite, ListInvites, ReadInvite, RevokeInvite
from dreamteams.application.manage_my_applications import (
    ListMyApplications,
    ReadMyApplication,
    WithdrawApplication,
)
from dreamteams.application.manage_profile import ReadProfile
from dreamteams.application.manage_profile.attach_avatar import AttachAvatar
from dreamteams.application.manage_profile.delete import DeleteProfile
from dreamteams.application.manage_profile.detach_avatar import DetachAvatar
from dreamteams.application.manage_profile.update_organizer import UpdateOrganizer
from dreamteams.application.manage_profile.update_participant import UpdateParticipant
from dreamteams.application.manage_tags import (
    CreateCompetitionTag,
    DeleteCompetitionTag,
    ReadCompetitionTag,
)
from dreamteams.application.manage_tags import ListCompetitionTags as ListCompetitionTagsAsAdmin
from dreamteams.application.manage_users import BlockUser, ListUsers, ReadUserByAdmin, UnblockUser
from dreamteams.application.preview_competition.list import PreviewCompetitions
from dreamteams.application.publish_competition import CreateCompetition
from dreamteams.application.register.register_organizer import RegisterOrganizer
from dreamteams.application.register.register_participant import RegisterParticipant
from dreamteams.application.register.register_superuser import RegisterSuperuser
from dreamteams.application.register.shared.user_factory import UserFactory
from dreamteams.application.submit_application import ExploreCompetitions, SubmitApplication
from dreamteams.application.submit_application import ReadApplicationForm as ReadApplicationFormAsParticipant
from dreamteams.application.submit_application import ReadCompetition as ReadCompetitionAsParticipant
from dreamteams.application.view_tags import ListCompetitionTags as ViewCompetitionTags


class InteractorProvider(Provider):
    """Dishka provider that registers all use case interactors for dependency injection."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        RegisterOrganizer,
        RegisterSuperuser,
        RegisterParticipant,
        ReadProfile,
        CreateCompetition,
        ListCompetitions,
        ReadCompetitionAsOrganizer,
        ReadCompetitionAsParticipant,
        DeleteCompetition,
        UpdateCompetition,
        AttachAvatar,
        DetachAvatar,
        UpdateParticipant,
        UpdateOrganizer,
        PreviewCompetitions,
        ExploreCompetitions,
        DeleteProfile,
        IssueInvite,
        ListInvites,
        ReadInvite,
        RevokeInvite,
        CreateApplicationForm,
        ReadApplicationFormAsOrganizer,
        ReadApplicationFormAsParticipant,
        DeleteApplicationForm,
        SubmitApplication,
        ReadMyApplication,
        ListMyApplications,
        WithdrawApplication,
        ReadApplication,
        ListApplicationsByCompetition,
        AcceptApplication,
        RejectApplication,
        BlockUser,
        UnblockUser,
        ListUsers,
        ReadUserByAdmin,
        CreateCompetitionTag,
        ReadCompetitionTag,
        ListCompetitionTagsAsAdmin,
        DeleteCompetitionTag,
        ViewCompetitionTags,
    )
    user_factory = provide(UserFactory)
