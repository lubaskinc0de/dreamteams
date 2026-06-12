import asyncio
from uuid import uuid4

from dreamteams.entities.application.entity import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_participant_can_withdraw_pending_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant who submitted a PENDING application can withdraw it successfully."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_status(200)


async def test_concurrent_withdraws_delete_application_once(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Concurrent withdraws of the same application delete it exactly once."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    async def withdraw() -> int:
        with api_client.authenticate(auth_user_id=participant.auth_id):
            return (await api_client.withdraw_application(application_id)).status

    # Act
    statuses = await asyncio.gather(withdraw(), withdraw())
    with api_client.authenticate(auth_user_id=participant.auth_id):
        read_response = await api_client.read_my_application(application_id)

    # Assert
    assert sorted(statuses) == [200, 404]
    read_response.assert_error(404, "APPLICATION_NOT_FOUND")


async def test_concurrent_withdraw_and_accept_resolve_application_once(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Concurrent withdraw and accept of the same application resolve it exactly once."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    async def withdraw() -> int:
        with api_client.authenticate(auth_user_id=participant.auth_id):
            return (await api_client.withdraw_application(application_id)).status

    async def accept() -> int:
        with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
            return (await api_client.accept_application(application_id)).status

    # Act
    withdraw_status, accept_status = await asyncio.gather(withdraw(), accept())
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        read_response = await api_client.read_application(application_id)

    # Assert
    assert withdraw_status == 200 or accept_status == 200
    assert not (withdraw_status == 200 and accept_status == 200)
    if withdraw_status == 200:
        assert accept_status == 404
        read_response.assert_error(404, "APPLICATION_NOT_FOUND")
    else:
        assert withdraw_status == 409
        actual = read_response.assert_status(200).ensure_content()
        assert actual.status == ApplicationStatus.ACCEPTED


async def test_concurrent_withdraw_and_reject_resolve_application_once(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Concurrent withdraw and reject of the same application resolve it exactly once."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    async def withdraw() -> int:
        with api_client.authenticate(auth_user_id=participant.auth_id):
            return (await api_client.withdraw_application(application_id)).status

    async def reject() -> int:
        with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
            return (await api_client.reject_application(application_id)).status

    # Act
    withdraw_status, reject_status = await asyncio.gather(withdraw(), reject())
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        read_response = await api_client.read_application(application_id)

    # Assert
    assert withdraw_status == 200 or reject_status == 200
    assert not (withdraw_status == 200 and reject_status == 200)
    if withdraw_status == 200:
        assert reject_status == 404
        read_response.assert_error(404, "APPLICATION_NOT_FOUND")
    else:
        assert withdraw_status == 409
        actual = read_response.assert_status(200).ensure_content()
        assert actual.status == ApplicationStatus.REJECTED


async def test_withdraw_application_fails_if_user_has_no_participant_role(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Withdrawing application fails when user has no participant role."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.withdraw_application(application_id)

    response.assert_error(404, "PARTICIPANT_NOT_FOUND")


async def test_unauthenticated_cannot_withdraw_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests to withdraw an application are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_other_participant_cannot_withdraw_application(
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
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_accepted_application_cannot_be_withdrawn(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A participant cannot withdraw an application that has already been accepted."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)
    await gateway.application.accept(application_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.withdraw_application(application_id)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_RESOLVED")


async def test_withdrawing_nonexistent_application_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Withdrawing an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    participant = await gateway.participant.create()
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.withdraw_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
