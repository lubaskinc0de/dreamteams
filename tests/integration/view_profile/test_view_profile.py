from dreamteams.application.register.organizer import CreatedOrganizer
from dreamteams.application.view_profile.interactor import OrganizerModel, ProfileModel
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.integration.api_client import ApiClient


async def test_view_organizer_profile(
    api_client: ApiClient,
    organizer: CreatedOrganizer,
    organizer_form: OrganizerForm,
    email: str,
) -> None:
    """Test view only organizer profile."""
    with api_client.authenticate(auth_user_id="1"):
        response = await api_client.view_profile()

    profile_model = response.assert_status(200).ensure_ok()
    assert profile_model == ProfileModel(
        user_id=organizer.user_id,
        organizer=OrganizerModel(
            id=organizer.organizer_id,
            user_id=organizer.user_id,
            organizer_name=organizer_form.organizer_name,
            phone_number=organizer_form.phone_number,
            contact_email=email,
            logo=None,
        ),
    )


async def test_view_organizer_profile_fails_if_user_does_not_exists(
    api_client: ApiClient,
) -> None:
    """Test view organizer profile fails if user does not exists."""
    with api_client.authenticate(auth_user_id="1"):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_organizer_profile_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test view organizer profile fails if user unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")
