from dataclasses import dataclass
from typing import override

from adaptix import ExtraSkip, Retort, name_mapping

from dreamteams.application.common.dto.application import ApplicationModel, ParticipantInfo
from dreamteams.application.manage_profile.read_profile import ProfileModel
from dreamteams.entities.application.entity import ApplicationStatus as MainApplicationStatus
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact as MainParticipantContact
from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.application_form_gateway import HttpApplicationFormGateway
from dreamteams_exporter.adapters.http.applications_gateway import HttpApplicationsGateway
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.application.common.dto.application import ApplicationsPage
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.application_form.entity import ApplicationForm, ApplicationFormField
from dreamteams_exporter.entities.common.identifiers import CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.common.vo.participant_contact import ParticipantContact
from dreamteams_exporter.entities.participant.entity import Participant
from dreamteams_exporter.entities.user import User
from tests.integration.api_client import ApiClient

_application_form_retort = Retort(
    recipe=[
        name_mapping(ApplicationForm, extra_in=ExtraSkip()),
        name_mapping(ApplicationFormField, extra_in=ExtraSkip()),
    ],
)


def _to_exporter_contact(contact: MainParticipantContact) -> ParticipantContact:
    return ParticipantContact(title=contact.title, value=contact.value)


def _to_exporter_participant(participant: ParticipantInfo) -> Participant:
    return Participant(
        id=participant.id,
        full_name=participant.full_name,
        bio=participant.bio,
        participant_type=participant.participant_type.value,
        age=participant.age,
        contacts=[_to_exporter_contact(c) for c in participant.contacts],
    )


def to_exporter_application(application: ApplicationModel) -> Application:
    """Map main application DTO into the exporter-local application projection."""
    return Application(
        id=application.id,
        competition_id=application.competition_id,
        competition_name=application.competition_name,
        track=application.track.name,
        status=ApplicationStatus(application.status.value),
        created_at=application.created_at,
        form_data=application.form_data,
        participant=_to_exporter_participant(application.participant),
    )


@dataclass(slots=True)
class FakeHttpUserGateway(HttpUserGateway):
    """Test replacement for the exporter's user gateway backed by the main app ApiClient."""

    api_client: ApiClient

    @override
    async def get_me(self, user_id: AuthUserId) -> User:
        """Resolve the caller's user projection from the main app."""
        with self.api_client.authenticate(auth_user_id=user_id):
            profile: ProfileModel = (await self.api_client.view_profile()).assert_status(200).ensure_content()

        return User(
            user_id=profile.user_id,
            organizer_id=profile.organizer.id if profile.organizer is not None else None,
            participant_id=profile.participant.id if profile.participant is not None else None,
        )


@dataclass(slots=True)
class FakeApplicationFormGateway(HttpApplicationFormGateway):
    """Test replacement for the exporter's application form gateway backed by ApiClient."""

    api_client: ApiClient
    user_id: AuthUserId

    @override
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Read the application form through the organizer endpoint."""
        with self.api_client.authenticate(auth_user_id=self.user_id):
            response = await self.api_client.read_application_form(competition_id)
            if (
                response.status == 404
                and response.error is not None
                and response.error.code == "APPLICATION_FORM_NOT_FOUND"
            ):
                return None
            payload = response.assert_status(200).ensure_content()

        return _application_form_retort.load(payload.model_dump(mode="json"), ApplicationForm)


@dataclass(slots=True)
class FakeApplicationsGateway(HttpApplicationsGateway):
    """Test replacement for the exporter's applications gateway backed by the main app ApiClient."""

    api_client: ApiClient
    user_id: AuthUserId

    @override
    async def list(
        self,
        *,
        competition_id: CompetitionId,
        status: ApplicationStatus | None,
        page: int,
        page_size: int,
    ) -> ApplicationsPage:
        """List applications through the main organizer endpoint and map them into exporter DTOs."""
        with self.api_client.authenticate(auth_user_id=self.user_id):
            response = await self.api_client.list_applications_by_competition(
                competition_id,
                page=page,
                page_size=page_size,
                status=MainApplicationStatus(status.value) if status is not None else None,
            )
            payload = response.assert_status(200).ensure_content()

        return ApplicationsPage(
            items=[to_exporter_application(item) for item in payload.items],
            page=payload.page,
            page_size=page_size,
            total=payload.total,
        )
