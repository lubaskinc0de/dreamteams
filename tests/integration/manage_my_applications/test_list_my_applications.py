import pytest

from dreamteams.application.manage_my_applications import ApplicationModel, ApplicationsList
from dreamteams.application.manage_my_applications.list import PAGE_SIZE
from dreamteams.entities.application.entity import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway
from tests.integration.manage_my_applications.helpers import create_my_applications_list


async def test_participant_can_list_own_applications(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant who submitted an application sees it in their application list."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationsList(
        items=[
            ApplicationModel(
                id=application_id,
                participant_id=result.items[0].participant_id,
                competition_id=comp.created.competition_id,
                domains=result.items[0].domains,
                status=ApplicationStatus.PENDING,
                created_at=result.items[0].created_at,
                form_data=None,
            ),
        ],
        total=1,
        page=1,
    )


@pytest.mark.parametrize("num_applications", [0, 1, 5, 10])
async def test_list_my_applications_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
    num_applications: int,
) -> None:
    """All own applications appear in the list regardless of their status."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    all_models = await gateway.application.submit_to_n_competitions(
        num_applications,
        owner.organizer.auth_id,
        participant.auth_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_my_applications_list(all_models)


async def test_participant_with_no_applications_gets_empty_list(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant who has not submitted any applications receives an empty list."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationsList(items=[], total=0, page=1)


async def test_unauthenticated_cannot_list_my_applications(
    api_client: ApiClient,
) -> None:
    """Unauthenticated requests to list own applications are rejected with UNAUTHORIZED."""
    # Act
    response = await api_client.list_my_applications()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_participant_cannot_list_applications(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A user without a participant profile is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_my_applications()

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


@pytest.mark.parametrize("page", [1, 2])
async def test_list_my_applications_with_pagination(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """List own applications returns the correct page and total when there are multiple pages of results."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    num_applications = page * PAGE_SIZE
    all_models = await gateway.application.submit_to_n_competitions(
        num_applications,
        owner.organizer.auth_id,
        participant.auth_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_my_applications(page=page)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_my_applications_list(all_models, page=page)


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_my_applications_with_invalid_page_fails(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Requesting an invalid page number is rejected with VALIDATION_ERROR."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_my_applications(page=page)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
