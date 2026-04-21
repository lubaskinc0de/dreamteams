import pytest

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.preview_competition.list import PAGE_SIZE, PreviewCompetitionsList
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competitions_list_to_preview_list, create_competitions_list
from tests.integration.helpers.facade import Gateway


async def test_preview_competitions_lists_active_competitions(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated user sees only active (open registration) competitions."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, 5)
    active = await gateway.competition.make_all_active(competitions, owner.organizer.auth_id)
    expected = competitions_list_to_preview_list(
        create_competitions_list(active, sort_by=CompetitionSortBy.CREATED_AT, sort_order=SortOrder.DESC),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    response = await api_client.list_preview_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == expected


async def test_preview_competitions_does_not_show_archived_competitions(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Archived competitions are hidden from the preview list."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, 5)
    await gateway.competition.change_archived_state(competitions, owner.organizer.auth_id, is_archived=True)

    # Act
    response = await api_client.list_preview_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == PreviewCompetitionsList(items=[], total=0, page=1)


async def test_preview_competitions_does_not_show_competitions_not_yet_begun(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competitions whose registration start is in the future are hidden from the preview list."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, 4)
    half = len(competitions) // 2
    active = await gateway.competition.make_all_active(competitions[:half], owner.organizer.auth_id)
    await gateway.competition.make_all_inactive(competitions[half:], owner.organizer.auth_id)
    expected = competitions_list_to_preview_list(
        create_competitions_list(active, sort_by=CompetitionSortBy.CREATED_AT, sort_order=SortOrder.DESC),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    response = await api_client.list_preview_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == expected


async def test_preview_competitions_does_not_show_competitions_with_closed_registration(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competitions whose registration end is in the past are hidden from the preview list."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, 4)
    half = len(competitions) // 2
    active = await gateway.competition.make_all_active(competitions[:half], owner.organizer.auth_id)
    await gateway.competition.make_all_passed(competitions[half:], owner.organizer.auth_id)
    expected = competitions_list_to_preview_list(
        create_competitions_list(active, sort_by=CompetitionSortBy.CREATED_AT, sort_order=SortOrder.DESC),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    response = await api_client.list_preview_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == expected


@pytest.mark.parametrize("page", [1, 2])
async def test_preview_competitions_pagination(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Preview competitions returns the correct page slice and total."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, page * PAGE_SIZE)
    active = await gateway.competition.make_all_active(competitions, owner.organizer.auth_id)
    all_preview = competitions_list_to_preview_list(
        create_competitions_list(
            active,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
            page_size=len(active),
        ),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    response = await api_client.list_preview_competitions(page)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == PreviewCompetitionsList(
        items=all_preview.items[(page - 1) * PAGE_SIZE : page * PAGE_SIZE],
        total=all_preview.total,
        page=page,
    )


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_preview_competitions_with_invalid_page_fails(
    api_client: ApiClient,
    page: int,
) -> None:
    """Requesting an invalid page number is rejected with VALIDATION_ERROR."""
    # Act
    response = await api_client.list_preview_competitions(page)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
