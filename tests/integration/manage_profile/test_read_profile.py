from dreamteams.application.manage_profile import OrganizerModel, ParticipantModel, ProfileModel
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant, ParticipantForm
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


async def test_view_organizer_profile(
    api_client: ApiClient,
    organizer: CreatedOrganizer,
    organizer_form: OrganizerForm,
    email: str,
) -> None:
    """Test viewing organizer profile."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.view_profile()

    profile_model = response.assert_status(200).ensure_content()
    assert profile_model == ProfileModel(
        user_id=organizer.user_id,
        organizer=OrganizerModel(
            id=organizer.organizer_id,
            user_id=organizer.user_id,
            organizer_name=organizer_form.organizer_name,
            phone_number=organizer_form.phone_number,
            contact_email=email,
        ),
        participant=None,
        avatar_url=None,
        is_admin=False,
    )


async def test_view_organizer_profile_fails_if_user_does_not_exist(
    api_client: ApiClient,
) -> None:
    """Test viewing organizer profile fails if user does not exist."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_organizer_profile_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test viewing organizer profile fails if user is unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_participant_profile(
    api_client: ApiClient,
    participant: CreatedParticipant,
    participant_form: ParticipantForm,
) -> None:
    """Test viewing participant profile."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.view_profile()

    profile_model = response.assert_status(200).ensure_content()
    assert profile_model == ProfileModel(
        user_id=participant.user_id,
        organizer=None,
        participant=ParticipantModel(
            id=participant.participant_id,
            user_id=participant.user_id,
            full_name=participant_form.full_name,
            bio=participant_form.bio,
            skills=[ParticipantSkill(name=s.name, level=s.level) for s in participant_form.skills],
            experience_level=participant_form.experience_level,
            preferred_domains=participant_form.preferred_domains,
            contacts=[ParticipantContact(title=c.title, url=str(c.url)) for c in participant_form.contacts],
        ),
        avatar_url=None,
        is_admin=False,
    )


async def test_view_participant_profile_fails_if_user_does_not_exist(
    api_client: ApiClient,
) -> None:
    """Test viewing participant profile fails if user does not exist."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_participant_profile_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test viewing participant profile fails if user is unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")
