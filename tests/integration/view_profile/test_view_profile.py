from posutochnik.application.register.landlord import CreatedLandlord
from posutochnik.application.view_profile.interactor import LandlordModel, ProfileModel
from posutochnik.presentation.fast_api.routers.landlords import LandlordForm
from tests.integration.api_client import ApiClient


async def test_view_landlord_profile(
    api_client: ApiClient,
    landlord: CreatedLandlord,
    landlord_form: LandlordForm,
    email: str,
) -> None:
    """Test view only landlord profile."""
    with api_client.authenticate(auth_user_id="1"):
        response = await api_client.view_profile()

    profile_model = response.assert_status(200).ensure_ok()
    assert profile_model == ProfileModel(
        user_id=landlord.user_id,
        landlord=LandlordModel(
            id=landlord.landlord_id,
            user_id=landlord.user_id,
            landlord_name=landlord_form.landlord_name,
            phone_number=landlord_form.phone_number,
            contact_email=email,
            avatar=None,
        ),
    )


async def test_view_landlord_profile_fails_if_user_does_not_exists(
    api_client: ApiClient,
) -> None:
    """Test view landlord profile fails if user does not exists."""
    with api_client.authenticate(auth_user_id="1"):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_landlord_profile_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test view landlord profile fails if user unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")
