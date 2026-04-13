from uuid import uuid4

from dreamteams.application.register.register_participant import CreatedParticipant
from dreamteams.application.submit_application import CreatedApplication
from tests.integration.api_client import ApiClient
from tests.integration.constants import ANOTHER_PARTICIPANT_USER_ID, PARTICIPANT_USER_ID, USER_ID


async def test_participant_can_withdraw_pending_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Participant who submitted a PENDING application can withdraw it successfully."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_status(200)


async def test_unauthenticated_cannot_withdraw_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """Unauthenticated requests to withdraw an application are rejected with UNAUTHORIZED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_other_participant_cannot_withdraw_application(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
    another_participant: CreatedParticipant,  # noqa: ARG001
) -> None:
    """A registered participant who did not submit the application is denied with ACCESS_DENIED."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=ANOTHER_PARTICIPANT_USER_ID):
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_accepted_application_cannot_be_withdrawn(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
) -> None:
    """A participant cannot withdraw an application that has already been accepted."""
    # Arrange — accept the application as the competition organizer
    application_id = submitted_application.application_id
    with api_client.authenticate(auth_user_id=USER_ID):
        (await api_client.accept_application(application_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_withdrawing_nonexistent_application_fails(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
) -> None:
    """Withdrawing an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.withdraw_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
