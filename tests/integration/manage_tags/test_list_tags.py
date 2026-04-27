from uuid import uuid4

import pytest

from dreamteams.application.manage_tags import CompetitionTagsList
from dreamteams.application.manage_tags.list import PAGE_SIZE
from dreamteams.entities.competition.tag import CompetitionTag
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


def _indexed_tag_values(prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{index:02d}" for index in range(count)]


def _create_tags_list(tags: list[CompetitionTag], page: int) -> CompetitionTagsList:
    sorted_tags = sorted(tags, key=lambda tag: tag.value)
    return CompetitionTagsList(
        items=sorted_tags[(page - 1) * PAGE_SIZE : page * PAGE_SIZE],
        total=len(tags),
        page=page,
    )


async def test_admin_can_list_tags_with_search(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can list competition tags matching a search value."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ListTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.list_admin_tags(search=tag.value)).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_admin_tag_search_is_case_insensitive(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin tag search matches values case-insensitively."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["CaseInsensitiveListTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.list_admin_tags(search=tag.value.lower())).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_admin_tag_search_ignores_surrounding_whitespace(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin tag search trims surrounding whitespace."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["WhitespaceSearchListTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.list_admin_tags(search=f"  {tag.value}  ")).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_admin_tag_list_returns_empty_result_for_unmatched_search(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin tag list returns an empty page when search matches no tags."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (
            (await api_client.list_admin_tags(search=f"MissingListTag-{uuid4()}")).assert_status(200).ensure_content()
        )

    # Assert
    assert actual == CompetitionTagsList(items=[], total=0, page=1)


@pytest.mark.parametrize("page", [1, 2])
async def test_admin_tag_list_paginates_with_fixed_page_size(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Admin tag list returns the requested page slice and total."""
    # Arrange
    admin = await gateway.admin.create()
    prefix = f"PagedListTag-{uuid4()}"
    tags = await gateway.tags.create_many(admin.auth_id, _indexed_tag_values(prefix, page * PAGE_SIZE))

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.list_admin_tags(page=page, search=prefix)).assert_status(200).ensure_content()

    # Assert
    assert actual == _create_tags_list(tags, page=page)


async def test_admin_tag_list_returns_empty_page_after_last_result(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin tag list returns an empty page when requested page is beyond matching results."""
    # Arrange
    admin = await gateway.admin.create()
    prefix = f"BeyondPageListTag-{uuid4()}"
    await gateway.tags.create_many(admin.auth_id, _indexed_tag_values(prefix, 2))

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.list_admin_tags(page=2, search=prefix)).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTagsList(items=[], total=2, page=2)


async def test_invalid_admin_tag_list_page_is_rejected(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin tag list rejects page numbers below 1."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_admin_tags(page=0)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_non_admin_cannot_list_admin_tags(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot list admin tags."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_admin_tags()

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_list_admin_tags(api_client: ApiClient) -> None:
    """Unauthenticated requests cannot list admin tags."""
    # Act
    response = await api_client.list_admin_tags()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
