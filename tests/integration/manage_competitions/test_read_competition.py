from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.publish_competition import CompetitionForm, CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.clock import Clock
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID
from tests.integration.manage_competitions.helpers import competition_form_to_model


async def test_read_competition_succeeds(
    api_client: ApiClient,
    competition: CreatedCompetition,
    competition_form: CompetitionForm,
    organizer: CreatedOrganizer,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Test reading competition by ID returns correct data."""
    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(competition.competition_id)
    expected_model = competition_form_to_model(
        competition.competition_id,
        organizer.organizer_id,
        db_competition.created_at,
        db_competition.updated_at,
        competition_form,
        clock=clock,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_competition(competition.competition_id)
        actual_model = response.assert_status(200).ensure_content()

    assert actual_model == expected_model


async def test_read_competition_with_non_existent_id_fails(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test reading competition with non-existent ID returns 404."""
    non_existent_id = uuid4()

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_competition(non_existent_id)

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_read_competition_by_different_organizer_fails(
    api_client: ApiClient,
    competition: CreatedCompetition,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test reading competition by different organizer returns 403."""
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.read_competition(competition.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_read_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Test reading competition without authentication returns 401."""
    response = await api_client.read_competition(competition.competition_id)

    response.assert_error(401, "UNAUTHORIZED")
