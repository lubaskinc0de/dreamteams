from uuid import uuid4

from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.submit_application import CreatedApplication
from dreamteams.entities.application.entity import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, PARTICIPANT_USER_ID, USER_ID


async def test_organizer_can_read_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
    active_non_autoaccept_competition: CreatedCompetition,
) -> None:
    """Competition organizer can read an application submitted to their competition."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application(application_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationModel(
        id=application_id,
        participant_id=result.participant_id,
        competition_id=active_non_autoaccept_competition.competition_id,
        domains=result.domains,
        status=ApplicationStatus.PENDING,
        created_at=result.created_at,
        form_data=None,
    )


async def test_unauthenticated_cannot_read_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Unauthenticated requests to read an application are rejected with UNAUTHORIZED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_read_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_withdrawn_application_cannot_be_read_by_organizer(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Reading a withdrawn application returns APPLICATION_NOT_FOUND for the organizer."""
    # Arrange — withdraw the application as the participant
    application_id = submitted_application.application_id
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        (await api_client.withdraw_application(application_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")


async def test_reading_nonexistent_application_fails(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Reading an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
