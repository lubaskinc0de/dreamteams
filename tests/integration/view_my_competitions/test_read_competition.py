from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams_common.clock import Clock
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_read_competition_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Test reading competition by ID returns correct data."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)

    expected_model = competition_form_to_model(
        form=comp.form,
        competition_id=comp.created.competition_id,
        organizer_id=owner.organizer.created.organizer_id,
        created_at=db_competition.created_at,
        updated_at=db_competition.updated_at,
        clock=clock,
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        actual_model = (
            (await api_client.read_competition(comp.created.competition_id)).assert_status(200).ensure_content()
        )

    # Assert
    assert actual_model == expected_model


async def test_read_competition_with_non_existent_id_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition with non-existent ID returns 404."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_competition(uuid4())

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_read_competition_by_different_organizer_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition by different organizer returns 403."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.read_competition(comp.created.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_read_competition_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition without authentication returns 401."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    response = await api_client.read_competition(comp.created.competition_id)

    response.assert_error(401, "UNAUTHORIZED")


async def test_competition_without_team_size_reads_back_as_null(
    gateway: Gateway,
    competition_form_factory: CompetitionFormFactory,
    clock: Clock,
) -> None:
    """A competition created with team_size=None and no team_formation reads back with all three as null."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    now = datetime.now(tz=UTC)
    form = competition_form_factory.build(
        team_size=None,
        schedule=ScheduleData(
            registration_start=now + timedelta(days=1),
            registration_end=now + timedelta(days=10),
            team_formation_start=None,
            team_formation_end=None,
        ),
    )

    # Act
    model = await gateway.competition.create_from_form(owner.organizer.auth_id, form)

    # Assert
    assert model == competition_form_to_model(
        competition_id=model.id,
        organizer_id=owner.organizer.created.organizer_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        form=form,
        clock=clock,
    )


@pytest.mark.parametrize("accepted_count", [0, 1, 5])
async def test_read_competition_returns_accepted_members_count(
    api_client: ApiClient,
    gateway: Gateway,
    accepted_count: int,
) -> None:
    """``members_count`` on the read response equals the number of ACCEPTED applications."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    [comp] = await gateway.application.create_active_competitions_with_accepted_members(
        owner.organizer.auth_id,
        [accepted_count],
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_competition(comp.created.competition_id)

    # Assert
    assert response.assert_status(200).ensure_content().members_count == accepted_count
