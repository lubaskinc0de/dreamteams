from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_organizer_can_reject_pending_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competition organizer can successfully reject a PENDING application."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reject_application(application_id)

    # Assert
    response.assert_status(200)


async def test_unauthenticated_cannot_reject_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests to reject an application are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    response = await api_client.reject_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_reject_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.reject_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_already_rejected_application_cannot_be_rejected_again(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Rejecting an application that has already been rejected is rejected with APPLICATION_ALREADY_RESOLVED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)
    await gateway.application.reject(application_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reject_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_accepted_application_cannot_be_rejected(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Rejecting an application that has already been accepted is rejected with APPLICATION_ALREADY_RESOLVED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)
    await gateway.application.accept(application_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reject_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_rejecting_nonexistent_application_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Rejecting an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reject_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
