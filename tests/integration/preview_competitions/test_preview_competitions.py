import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.preview_competition.list import PreviewCompetitionsList
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import (
    change_archived_state,
    competitions_list_to_preview_list,
    create_competitions_list,
    make_all_active,
    make_all_inactive,
    make_all_passed,
)


async def test_preview_competitions_lists_active_competitions(
    api_client: ApiClient,
    session: AsyncSession,
    competitions: list[CompetitionModel],
    organizer_form: OrganizerForm,
    organizer: CreatedOrganizer,
) -> None:
    """Test listing competitions as unauthorized user shows only active competitions."""
    expected_entries = await make_all_active(session, api_client, competitions)
    expected_model = competitions_list_to_preview_list(
        create_competitions_list(
            expected_entries,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        organizer_form,
        organizer.organizer_id,
    )

    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_preview_competitions_does_not_shows_archived_competitions(
    api_client: ApiClient,
    session: AsyncSession,
    competitions: list[CompetitionModel],
) -> None:
    """Test listing competitions as unauthorized user does not show archived competitions."""
    await change_archived_state(session, api_client, competitions, is_archived=True)
    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()

    assert result == PreviewCompetitionsList(items=[], total=0, page=1)  # all archived


async def test_preview_competitions_does_not_shows_competitions_which_not_begin(
    api_client: ApiClient,
    session: AsyncSession,
    competitions: list[CompetitionModel],
    organizer_form: OrganizerForm,
    organizer: CreatedOrganizer,
) -> None:
    """Test listing competitions as unauthorized user does not show competitions with reg start in future."""
    half = len(competitions) // 2
    expected_entries = await make_all_active(session, api_client, competitions[:half])
    await make_all_inactive(session, api_client, competitions[half:])
    expected_model = competitions_list_to_preview_list(
        create_competitions_list(
            expected_entries,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        organizer_form,
        organizer.organizer_id,
    )

    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_preview_competitions_does_not_shows_competitions_which_closed_registration(
    api_client: ApiClient,
    session: AsyncSession,
    competitions: list[CompetitionModel],
    organizer_form: OrganizerForm,
    organizer: CreatedOrganizer,
) -> None:
    """Test listing competitions as unauthorized user does not show competitions with reg end in past."""
    expected_entries = await make_all_active(session, api_client, competitions[: len(competitions) // 2])
    await make_all_passed(session, api_client, competitions[len(competitions) // 2 :])
    expected_model = competitions_list_to_preview_list(
        create_competitions_list(
            expected_entries,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        organizer_form,
        organizer.organizer_id,
    )

    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_preview_competitions_pagination(
    api_client: ApiClient,
    session: AsyncSession,
    competitions: list[CompetitionModel],
    organizer_form: OrganizerForm,
    organizer: CreatedOrganizer,
    page: int,
) -> None:
    """Preview competitions pagination must return correct items per page."""
    expected = await make_all_active(session, api_client, competitions)
    expected_model = competitions_list_to_preview_list(
        create_competitions_list(
            expected,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        organizer_form,
        organizer.organizer_id,
    )

    response = await api_client.list_preview_competitions(page)

    result = response.assert_status(200).ensure_content()
    assert result == PreviewCompetitionsList(
        items=expected_model.items[(page - 1) * 10 : page * 10],
        total=expected_model.total,
        page=page,
    )


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_competitions_with_invalid_pagination_fails(
    api_client: ApiClient,
    page: int,
) -> None:
    """Test listing competitions with invalid pagination fails."""
    response = await api_client.list_preview_competitions(page)

    response.assert_error(422, "VALIDATION_ERROR")
