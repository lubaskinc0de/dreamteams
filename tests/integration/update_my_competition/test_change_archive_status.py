from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.update_my_competition import ChangeCompetitionArchiveStatusForm
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_archive_status_change_as_owner_succeeds(
    gateway: Gateway,
    request_container: AsyncContainer,
) -> None:
    """Archive status change succeeds for the owning organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    current_model = await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id)
    expected_model = current_model.model_copy(update={"is_archived": False, "updated_at": db_competition.updated_at})

    # Act
    actual_model = await gateway.competition.change_archive_status(
        comp.created.competition_id,
        ChangeCompetitionArchiveStatusForm(is_archived=False),
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_archive_status_change_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Archive status change fails when user is unauthorized."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = ChangeCompetitionArchiveStatusForm(is_archived=False).model_dump(mode="json")

    # Act
    response = await api_client.change_competition_archive_status(comp.created.competition_id, data)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_archive_status_change_fails_if_not_owner(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Archive status change fails when user is not the owner."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = ChangeCompetitionArchiveStatusForm(is_archived=False).model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.change_competition_archive_status(comp.created.competition_id, data)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_archive_status_change_fails_if_not_found(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Archive status change fails when competition does not exist."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = ChangeCompetitionArchiveStatusForm(is_archived=False).model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.change_competition_archive_status(uuid4(), data)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")
