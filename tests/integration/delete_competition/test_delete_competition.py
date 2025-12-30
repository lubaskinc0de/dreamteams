from faker import Faker

from dreamteams.application.create_competition.interactor import CreatedCompetition
from dreamteams.application.register.organizer import CreatedOrganizer
from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient

# Test user IDs for authentication
USER_ID_FIRST = "1"
USER_ID_SECOND = "2"


async def test_delete_competition_as_owner_succeeds(
    api_client: ApiClient,
    competition: CreatedCompetition,
    email: str,
) -> None:
    """Test deleting competition by owner organizer."""
    with api_client.authenticate(auth_user_id=USER_ID_FIRST, auth_user_email=email):
        response = await api_client.delete_competition(competition.competition_id)

    response.assert_status(200)


async def test_delete_competition_fails_if_not_found(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    email: str,
    faker: Faker,
) -> None:
    """Test deleting non-existent competition."""
    non_existent_id = faker.uuid4(cast_to=None)

    with api_client.authenticate(auth_user_id=USER_ID_FIRST, auth_user_email=email):
        response = await api_client.delete_competition(non_existent_id)

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_delete_competition_fails_if_not_owner(
    api_client: ApiClient,
    competition: CreatedCompetition,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test deleting competition by different organizer."""
    second_organizer_email = faker.email()
    second_organizer_form = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id=USER_ID_SECOND, auth_user_email=second_organizer_email):
        (await api_client.register_organizer(second_organizer_form.model_dump())).assert_status(200)
        response = await api_client.delete_competition(competition.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_delete_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Test deleting competition fails when user is unauthorized."""
    response = await api_client.delete_competition(competition.competition_id)

    response.assert_error(401, "UNAUTHORIZED")
