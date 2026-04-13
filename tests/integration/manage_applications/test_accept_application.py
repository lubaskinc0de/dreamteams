from uuid import uuid4

from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.submit_application import CreatedApplication
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID


async def test_organizer_can_accept_pending_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Competition organizer can successfully accept a PENDING application."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.accept_application(application_id)

    # Assert
    response.assert_status(200)


async def test_unauthenticated_cannot_accept_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Unauthenticated requests to accept an application are rejected with UNAUTHORIZED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    response = await api_client.accept_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_accept_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.accept_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_already_accepted_application_cannot_be_accepted_again(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Accepting an application that has already been accepted is rejected with APPLICATION_ALREADY_RESOLVED."""
    # Arrange — accept the application first
    application_id = submitted_application.application_id
    with api_client.authenticate(auth_user_id=USER_ID):
        (await api_client.accept_application(application_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.accept_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_rejected_application_cannot_be_accepted(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Accepting an application that has already been rejected is rejected with APPLICATION_ALREADY_RESOLVED."""
    # Arrange — reject the application first
    application_id = submitted_application.application_id
    with api_client.authenticate(auth_user_id=USER_ID):
        (await api_client.reject_application(application_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.accept_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_accepting_nonexistent_application_fails(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Accepting an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.accept_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
