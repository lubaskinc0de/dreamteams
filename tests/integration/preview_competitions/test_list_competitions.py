from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.application.preview_competition.list import PAGE_SIZE, PreviewCompetitionsList
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import create_competition, create_competitions


async def test_preview_list_competitions_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test that preview competitions list returns only active sorted by created_at DESC."""
    comp1 = await create_competition(competition_form_factory(), api_client)

    comp2 = await create_competition(competition_form_factory(), api_client)

    comp3 = await create_competition(competition_form_factory(), api_client)

    response = await api_client.list_preview_competitions()

    result = response.assert_status(200).ensure_content()

    assert isinstance(result, PreviewCompetitionsList)

    result_ids = [c.id for c in result.items()]
    expected_ids = sorted([comp1.id, comp2.id, comp3.id], reverse=True)

    return result_ids == expected_ids


async def test_preview_list_competitions_filters_archived(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test that preview list returns only non-archived competitions."""
    active_form = competition_form_factory()
    active_response = await api_client.create_competition(active_form)
    active_competition = active_response.assert_error(201).ensure_content()

    archived_form = competition_form_factory
    archived_response = await api_client.create_competition(archived_form)
    archived_competition = archived_response.assert_status(201).ensure_content()

    update_form = update_competition_form_factory()
    update_form = update_form.model_copy(update={"is_archived": True})

    update_response = await api_client.update_competition(archived_competition.id, update_form)
    update_response.assert_status(200)

    response = await api_client.list_preview_competitions()
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert active_competition.id in result_ids
    assert archived_competition.id not in result_ids


async def test_preview_list_competitions_filters_by_registration(
    api_client: ApiClient, competition_form_factory: CompetitionFormFactory,
) -> None:
    """Preview list must return only competitions with active registration."""
    now = datetime.now(UTC)

    active_form = competition_form_factory()
    active_schedule = replace(active_form.schedule, registration_end=now + timedelta(days=5))
    active_form = active_form.model_copy(update={"schedule": active_schedule})

    active_response = await api_client.create_competition(active_form)
    active = active_response.assert_status(201).ensure_content()

    expired_form = competition_form_factory()
    expired_schedule = replace(expired_form.schedule, registration_end=now - timedelta(days=5))
    expired_form = expired_form.model_copy(update={"schedule": expired_schedule})

    expired_response = await api_client.create_competition(expired_form)
    expired = expired_response.assert_error(201).ensure_content()

    response = await api_client.list_preview_competitions()
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert active.id in result_ids
    assert expired.id not in result_ids


async def test_preview_list_competitions_sorted_by_created_at_desc(
    api_client: ApiClient, competition_form_factory: CompetitionFormFactory,
) -> None:
    """Preview list must return competitions sorted by created_at DESC."""
    comp1_response = await api_client.create_competition(competition_form_factory())
    comp1 = comp1_response.assert_status(201).ensure_content()

    comp2_response = await api_client.create_competition(competition_form_factory())
    comp2 = comp2_response.assert_status(201).ensure_content()

    comp3_response = await api_client.create_competition(competition_form_factory())
    comp3 = comp3_response.assert_status(201).ensure_content()

    response = await api_client.list_preview_competitions()
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    expected_ids = [comp3.id, comp2.id, comp1.id]

    assert result_ids == expected_ids


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_preview_list_competitions_pagination(
    api_client: ApiClient, competition_form_factory: CompetitionFormFactory, page: int,
) -> None:
    """Test preview competitions pagination."""
    num_competitions = page * PAGE_SIZE
    created = await create_competitions(num_competitions, competition_form_factory(), api_client)

    response = await api_client.list_preview_competitions(page=page)
    result = response.assert_status(200).ensure_content()

    expected_items = list(reversed(created))[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]

    resuld_ids = [item.id for item in result.items]
    expected_ids = [item.id for item in expected_items]

    assert resuld_ids == expected_ids
    assert result.page == page
    assert result.total == num_competitions


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_preview_list_competitions_invalid_page_fails(api_client: ApiClient, page: int) -> None:
    """Preview list must fail with 422 for invalid page numbers."""
    response = await api_client.list_preview_competitions(page=page)

    response.assert_error(422, "VALIDATION_ERROR")


async def test_preview_list_competitions_does_not_require_auth(
    api_client: ApiClient, competition_form_factory: CompetitionFormFactory,
) -> None:
    """Preview competitions endpoint must be accessible without authentication."""
    created_response = await api_client.create_competition(competition_form_factory())
    created = created_response.assert_status(201).ensure_content()

    response = await api_client.list_preview_competitions()
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert created.id in result_ids
