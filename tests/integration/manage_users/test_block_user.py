from uuid import uuid4

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competitions_list_to_preview_list, create_competitions_list
from tests.integration.helpers.facade import Gateway
from tests.integration.manage_applications.helpers import create_applications_list


async def test_admin_can_block_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can block a user account."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.block_user(participant.created.user_id, {"reason": "policy"})

    # Assert
    response.assert_status(200)


async def test_blocked_user_gets_account_blocked_on_next_request(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Blocked users receive ACCOUNT_BLOCKED on their next authenticated request."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        (await api_client.block_user(participant.created.user_id, {"reason": "policy"})).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.view_profile()

    # Assert
    response.assert_error(403, "ACCOUNT_BLOCKED")


async def test_block_includes_reason_in_error_meta(api_client: ApiClient, gateway: Gateway) -> None:
    """Blocked user errors include the block reason in meta."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    reason = "Repeated abuse"
    with api_client.authenticate(auth_user_id=admin.auth_id):
        (await api_client.block_user(participant.created.user_id, {"reason": reason})).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.view_profile()

    # Assert
    error = response.assert_error(403, "ACCOUNT_BLOCKED").ensure_err()
    assert error.meta is not None
    assert error.meta["reason"] == reason


async def test_non_admin_cannot_block_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Organizer users cannot block accounts."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.block_user(participant.created.user_id, {"reason": "policy"})

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_block_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Unauthenticated requests cannot block accounts."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    response = await api_client.block_user(participant.created.user_id, {"reason": "policy"})

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_block_nonexistent_user_returns_not_found(api_client: ApiClient, gateway: Gateway) -> None:
    """Blocking an unknown user returns USER_NOT_FOUND."""
    # Arrange
    admin = await gateway.admin.create()
    nonexistent_user_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.block_user(nonexistent_user_id, {"reason": "policy"})

    # Assert
    response.assert_error(404, "USER_NOT_FOUND")


async def test_blocked_organizers_competitions_hidden_from_preview(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Preview competitions exclude competitions owned by blocked organizers."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    visible_owner = await gateway.organizer.create(owner.admin.auth_id)
    hidden_competitions = await gateway.competition.create_many(owner.organizer.auth_id, 2)
    visible_competitions = await gateway.competition.create_many(visible_owner.auth_id, 2)
    await gateway.competition.make_all_active(hidden_competitions, owner.organizer.auth_id)
    visible_active = await gateway.competition.make_all_active(visible_competitions, visible_owner.auth_id)
    expected = competitions_list_to_preview_list(
        create_competitions_list(
            visible_active,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        visible_owner.form,
        visible_owner.created.organizer_id,
    )
    with api_client.authenticate(auth_user_id=owner.admin.auth_id):
        (await api_client.block_user(owner.organizer.created.user_id, {"reason": "policy"})).assert_status(200)

    # Act
    response = await api_client.list_preview_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == expected


async def test_blocked_participants_applications_hidden_from_list(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Application lists exclude applications submitted by blocked participants."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    visible_participant = await gateway.participant.create()
    blocked_participant = await gateway.participant.create()
    visible_application_id = await gateway.application.submit(visible_participant.auth_id, competition)
    await gateway.application.submit(blocked_participant.auth_id, competition)
    visible_application = await gateway.application.read_as_organizer(
        visible_application_id,
        owner.organizer.auth_id,
    )
    expected = create_applications_list([visible_application])
    with api_client.authenticate(auth_user_id=owner.admin.auth_id):
        (await api_client.block_user(blocked_participant.created.user_id, {"reason": "policy"})).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(competition.created.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == expected
