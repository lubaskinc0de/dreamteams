from dreamteams.application.manage_profile import OrganizerModel, ProfileModel
from dreamteams.application.register.register_organizer import CreatedOrganizer
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
        avatar_url=None,
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
