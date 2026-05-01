from uuid import uuid4

import pytest

from dreamteams.application.common.input_limits import MAX_PAGE, MAX_SEARCH_LENGTH
from dreamteams.application.view_tags import CompetitionTagsList
from dreamteams.application.view_tags.list_tags import PAGE_SIZE
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


async def test_participant_can_list_tags_with_search(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant can search the tag catalog."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ParticipantVisibleTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(search=tag.value)

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_organizer_can_list_tags_with_search(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Organizer can search the tag catalog."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    tag = (await gateway.tags.create_many_unique(owner.admin.auth_id, ["OrganizerVisibleTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_tags(search=tag.value)

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_participant_tag_search_is_case_insensitive(api_client: ApiClient, gateway: Gateway) -> None:
    """Participant tag search matches values case-insensitively."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ParticipantCaseSearchTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(search=tag.value.lower())

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_participant_tag_search_ignores_surrounding_whitespace(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant tag search trims surrounding whitespace."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ParticipantWhitespaceSearchTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(search=f"  {tag.value}  ")

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[tag], total=1, page=1)


async def test_participant_tag_list_returns_empty_result_for_unmatched_search(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant tag list returns an empty page when search matches no tags."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(search=f"MissingVisibleTag-{uuid4()}")

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[], total=0, page=1)


@pytest.mark.parametrize("page", [1, 2])
async def test_participant_tag_list_paginates_with_fixed_page_size(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Participant tag list returns the requested page slice and total."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    prefix = f"VisiblePagedTag-{uuid4()}"
    tags = await gateway.tags.create_many(admin.auth_id, _indexed_tag_values(prefix, page * PAGE_SIZE))

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(page=page, search=prefix)

    # Assert
    assert response.assert_status(200).ensure_content() == _create_tags_list(tags, page=page)


async def test_participant_tag_list_returns_empty_page_after_last_result(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant tag list returns an empty page when requested page is beyond matching results."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    prefix = f"VisibleBeyondPageTag-{uuid4()}"
    await gateway.tags.create_many(admin.auth_id, _indexed_tag_values(prefix, 2))

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(page=2, search=prefix)

    # Assert
    assert response.assert_status(200).ensure_content() == CompetitionTagsList(items=[], total=2, page=2)


async def test_unauthenticated_user_cannot_list_tags(api_client: ApiClient) -> None:
    """Unauthenticated requests to view tags are rejected."""
    # Act
    response = await api_client.list_tags()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_invalid_visible_tag_list_page_is_rejected(api_client: ApiClient, gateway: Gateway) -> None:
    """Visible tag list rejects page numbers below 1."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(page=0)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_visible_tag_list_rejects_too_large_page(api_client: ApiClient, gateway: Gateway) -> None:
    """Visible tag list rejects page numbers above the configured cap."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(page=MAX_PAGE + 1)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_visible_tag_list_rejects_too_long_search(api_client: ApiClient, gateway: Gateway) -> None:
    """Visible tag list rejects oversized search values before using them in SQL and cache keys."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_tags(search="a" * (MAX_SEARCH_LENGTH + 1))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
