from faker import Faker

from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.conftest import DIFFERENT_USER_ID, USER_ID


async def test_delete_competition_as_owner_succeeds(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Test deleting competition by owner organizer."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_competition(competition.competition_id)

    response.assert_status(200)


async def test_delete_competition_fails_if_not_found(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    faker: Faker,
) -> None:
    """Test deleting non-existent competition."""
    non_existent_id = faker.uuid4(cast_to=None)

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_competition(non_existent_id)

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_delete_competition_fails_if_not_owner(
    api_client: ApiClient,
    competition: CreatedCompetition,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test deleting competition by different organizer."""
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.delete_competition(competition.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_delete_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Test deleting competition fails when user is unauthorized."""
    response = await api_client.delete_competition(competition.competition_id)

    response.assert_error(401, "UNAUTHORIZED")
