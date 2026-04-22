from uuid import uuid4

from dreamteams.application.manage_my_applications import MyApplicationModel
from dreamteams.entities.application.entity import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_participant_can_read_own_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant who submitted an application can read it and receives the full MyApplicationModel."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_my_application(application_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == MyApplicationModel(
        id=application_id,
        participant_id=result.participant_id,
        competition_id=comp.created.competition_id,
        competition_name=comp.form.title,
        domains=result.domains,
        status=ApplicationStatus.PENDING,
        created_at=result.created_at,
        form_data=None,
    )


async def test_unauthenticated_cannot_read_my_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests to read an application are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    response = await api_client.read_my_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_other_participant_cannot_read_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A registered participant who did not submit the application is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    submitter = await gateway.participant.create()
    other_participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(submitter.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=other_participant.auth_id):
        response = await api_client.read_my_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_withdrawn_application_cannot_be_read(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a withdrawn application returns APPLICATION_NOT_FOUND for the participant."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)
    await gateway.application.withdraw(application_id, participant.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_my_application(application_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")


async def test_reading_nonexistent_application_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    participant = await gateway.participant.create()
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_my_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
