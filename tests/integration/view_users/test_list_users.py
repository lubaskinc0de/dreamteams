import pytest

from dreamteams.application.block_user import AdminUserListItem, UsersList
from dreamteams.application.common.gateway.user import UserRoleFilter
from dreamteams.application.common.input_limits import MAX_PAGE, MAX_SEARCH_LENGTH
from dreamteams.application.view_users.list_users import PAGE_SIZE
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.models import AdminCreated


def _admin_list_item(user_id: UserId) -> AdminUserListItem:
    return AdminUserListItem(
        id=user_id,
        is_admin=True,
        ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
        organizer_name=None,
        participant_full_name=None,
    )


def _sort_admins_for_list(admins: list[AdminCreated]) -> list[AdminCreated]:
    admins_by_id = sorted(admins, key=lambda item: item.user_id)
    return sorted(admins_by_id, key=lambda item: item.created_at, reverse=True)


def create_admin_users_list(
    admins: list[AdminCreated],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> UsersList:
    """Build paginated ``UsersList`` for admin-only users with default list sorting."""
    sorted_admins = _sort_admins_for_list(admins)
    start = (page - 1) * page_size
    paginated = sorted_admins[start : start + page_size]
    return UsersList(
        items=[_admin_list_item(admin.user_id) for admin in paginated],
        total=len(admins),
        page=page,
    )


async def test_admin_can_list_users_with_role_and_ban_summaries(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin user lists include organizer, participant, admin, and ban summaries."""
    # Arrange
    admin = await gateway.admin.create()
    organizer = await gateway.organizer.create(admin.auth_id)
    participant = await gateway.participant.create()
    reason = "policy"
    await gateway.admin.block_user(admin.auth_id, participant.created.user_id, reason=reason)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users()

    # Assert
    result = response.assert_status(200).ensure_content()
    participant_item = next(item for item in result.items if item.id == participant.created.user_id)
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=participant.created.user_id,
                is_admin=False,
                ban_status=BanStatus(
                    is_blocked=True,
                    reason=reason,
                    blocked_at=participant_item.ban_status.blocked_at,
                ),
                organizer_name=None,
                participant_full_name=participant.form.full_name,
            ),
            AdminUserListItem(
                id=organizer.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=organizer.form.organizer_name,
                participant_full_name=None,
            ),
            AdminUserListItem(
                id=admin.user_id,
                is_admin=True,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=None,
                participant_full_name=None,
            ),
        ],
        total=3,
        page=1,
    )


async def test_admin_user_list_filters_by_admin_flag(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin flag filter returns only admin users."""
    # Arrange
    admin = await gateway.admin.create()
    await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(is_admin=True)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=admin.user_id,
                is_admin=True,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=None,
                participant_full_name=None,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_filters_by_blocked_status(api_client: ApiClient, gateway: Gateway) -> None:
    """Blocked status filter returns only blocked users."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    reason = "policy"
    await gateway.admin.block_user(admin.auth_id, participant.created.user_id, reason=reason)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(is_blocked=True)

    # Assert
    result = response.assert_status(200).ensure_content()
    blocked_item = result.items[0]
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=participant.created.user_id,
                is_admin=False,
                ban_status=BanStatus(
                    is_blocked=True,
                    reason=reason,
                    blocked_at=blocked_item.ban_status.blocked_at,
                ),
                organizer_name=None,
                participant_full_name=participant.form.full_name,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_filters_by_organizer_role(api_client: ApiClient, gateway: Gateway) -> None:
    """Organizer role filter returns only organizer users."""
    # Arrange
    admin = await gateway.admin.create()
    organizer = await gateway.organizer.create(admin.auth_id)
    await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(role=UserRoleFilter.ORGANIZER)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=organizer.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=organizer.form.organizer_name,
                participant_full_name=None,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_filters_by_participant_role(api_client: ApiClient, gateway: Gateway) -> None:
    """Participant role filter returns only participant users."""
    # Arrange
    admin = await gateway.admin.create()
    await gateway.organizer.create(admin.auth_id)
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(role=UserRoleFilter.PARTICIPANT)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=participant.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=None,
                participant_full_name=participant.form.full_name,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_searches_by_organizer_name(api_client: ApiClient, gateway: Gateway) -> None:
    """Organizer name search returns matching organizer users."""
    # Arrange
    admin = await gateway.admin.create()
    organizer = await gateway.organizer.create(admin.auth_id, organizer_name="OrganizerSearchNeedle")
    await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(search=organizer.form.organizer_name.swapcase())

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=organizer.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=organizer.form.organizer_name,
                participant_full_name=None,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_searches_by_participant_full_name(api_client: ApiClient, gateway: Gateway) -> None:
    """Participant full-name search returns matching participant users."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(search=participant.form.full_name.swapcase())

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=participant.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=None,
                participant_full_name=participant.form.full_name,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_searches_by_user_id(api_client: ApiClient, gateway: Gateway) -> None:
    """User ID search returns the matching user."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(search=str(participant.created.user_id))

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == UsersList(
        items=[
            AdminUserListItem(
                id=participant.created.user_id,
                is_admin=False,
                ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
                organizer_name=None,
                participant_full_name=participant.form.full_name,
            ),
        ],
        total=1,
        page=1,
    )


async def test_admin_user_list_returns_empty_page_when_no_users_match(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin user list returns an empty page when filters match no users."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(search="does-not-exist")

    # Assert
    assert response.assert_status(200).ensure_content() == UsersList(items=[], total=0, page=1)


@pytest.mark.parametrize("page", [1, 2])
async def test_admin_user_list_paginates_with_fixed_page_size(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Admin user list returns pages of twenty users and reports the full total."""
    # Arrange
    admins = await gateway.admin.create_many(page * PAGE_SIZE)
    auth_admin = admins[0]

    # Act
    with api_client.authenticate(auth_user_id=auth_admin.auth_id):
        response = await api_client.list_admin_users(page=page)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_admin_users_list(admins, page=page)


async def test_non_admin_cannot_list_users(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot list users."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_admin_users()

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_list_users(api_client: ApiClient) -> None:
    """Unauthenticated requests cannot list users."""
    # Act
    response = await api_client.list_admin_users()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_admin_user_list_rejects_invalid_filters(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin user list rejects invalid page and role filter values."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        page_response = await api_client.list_admin_users(page=0)
        role_response = await api_client.list_admin_users(role="invalid")

    # Assert
    page_response.assert_error(422, "VALIDATION_ERROR")
    role_response.assert_error(422, "VALIDATION_ERROR")


async def test_admin_user_list_rejects_too_large_page(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin user list rejects page numbers above the configured cap."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(page=MAX_PAGE + 1)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_admin_user_list_rejects_too_long_search(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin user list rejects oversized search strings before building LIKE predicates."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_users(search="a" * (MAX_SEARCH_LENGTH + 1))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
