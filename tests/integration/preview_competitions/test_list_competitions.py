from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.application.preview_competition.list import PAGE_SIZE, PreviewCompetitionsList
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.conftest import create_competition, create_competitions, USER_ID



async def test_preview_list_competitions_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test that preview competitions list returns only active sorted by created_at DESC."""
    now = datetime.now(UTC)
    
    def active_form():
        form = competition_form_factory.build()
        schedule = replace(
            form.schedule,
            registration_start=now,
            registration_end=now + timedelta(days=5),
        )
        return form.model_copy(update={'schedule': schedule, 'is_archived': False})
    
    
    with api_client.authenticate(auth_user_id=USER_ID):
        comp1 = await create_competition(active_form(), api_client)
        comp2 = await create_competition(active_form(), api_client)
        comp3 = await create_competition(active_form(), api_client)

        response = await api_client.list_preview_competitions()

    result = response.assert_status(200).ensure_content()

    assert isinstance(result, PreviewCompetitionsList)

    result_ids = [c.id for c in result.items]
    expected_ids = sorted([comp1.id, comp2.id, comp3.id], reverse=True)

    assert result_ids == expected_ids


async def test_preview_list_competitions_filters_archived(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test that preview list returns only non-archived competitions."""
    now = datetime.now(UTC)
    
    with api_client.authenticate(auth_user_id=USER_ID):
        active_form = competition_form_factory.build() 
        schedule = replace(
            active_form.schedule,
            registration_start=now,
            registration_end=now + timedelta(days=5),
        )
        active_competition = await create_competition(
            active_form.model_copy(update={'schedule': schedule}),
            api_client)

        archived_form = competition_form_factory.build()
        schedule = replace(
            active_form.schedule,
            registration_start=now - timedelta(days=6),
            registration_end=now - timedelta(days=1),
        )
        archived_competition = await create_competition(
            archived_form.model_copy(update={'schedule': schedule}),
            api_client)
        
        await api_client.update_competition(archived_competition.id, {'is_archived': True})

        response = await api_client.list_preview_competitions()
        
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert active_competition.id in result_ids
    assert archived_competition.id not in result_ids


async def test_preview_list_competitions_filters_by_registration(
    api_client: ApiClient, 
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Preview list must return only competitions with active registration."""
    
    now = datetime.now(UTC)
    
    with api_client.authenticate(auth_user_id=USER_ID):
        active_form = competition_form_factory.build()
        active_schedule = replace(active_form.schedule, registration_end=now + timedelta(days=5))
        active_form = active_form.model_copy(update={"schedule": active_schedule})

        active = await create_competition(active_form, api_client)

        expired_form = competition_form_factory.build()
        expired_schedule = replace(
            expired_form.schedule,
            registration_start=now + timedelta(days=1),
            registration_end=now + timedelta(days=5),
        )
        expired_form = expired_form.model_copy(update={"schedule": expired_schedule})

        expired = await create_competition(expired_form, api_client)

        response = await api_client.list_preview_competitions()
        
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert active.id in result_ids
    assert expired.id not in result_ids


async def test_preview_list_competitions_sorted_by_created_at_desc(
    api_client: ApiClient, 
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Preview list must return competitions sorted by created_at DESC."""
    now = datetime.now(UTC)
    
    def active_form():
        form = competition_form_factory.build()
        schedule = replace(
            form.schedule,
            registration_start=now,
            registration_end=now + timedelta(days=5),
        )
        return form.model_copy(update={'schedule': schedule})
    
    with api_client.authenticate(auth_user_id=USER_ID):
        comp1 = await create_competition(active_form(), api_client)
        comp2 = await create_competition(active_form(), api_client)
        comp3 = await create_competition(active_form(), api_client)

    response = await api_client.list_preview_competitions()
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    expected_ids = [comp3.id, comp2.id, comp1.id]

    assert result_ids == expected_ids


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_preview_list_competitions_pagination(
    api_client: ApiClient, 
    competition_form_factory: CompetitionFormFactory,
    page: int,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test preview competitions pagination."""
    num_competitions = page * PAGE_SIZE
    
    with api_client.authenticate(auth_user_id=USER_ID):
        created = await create_competitions(num_competitions, competition_form_factory.build(), api_client)

    response = await api_client.list_preview_competitions(page=page)
        
    result = response.assert_status(200).ensure_content()

    expected_items = list(reversed(created))[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]

    result_ids = [item.id for item in result.items]
    expected_ids = [item.id for item in expected_items]

    assert result_ids == expected_ids
    assert result.page == page
    assert result.total == num_competitions


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_preview_list_competitions_invalid_page_fails(
    api_client: ApiClient,
    page: int,
    organizer: CreatedOrganizer,  # noqa: ARG001
    ) -> None:
    """Preview list must fail with 422 for invalid page numbers."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_preview_competitions(page=page)

    response.assert_error(422, "VALIDATION_ERROR")


async def test_preview_list_competitions_does_not_require_auth(
    api_client: ApiClient, 
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Preview competitions endpoint must be accessible without authentication."""
    now = datetime.now(UTC)
    
    with api_client.authenticate(auth_user_id=USER_ID):
        active_form = competition_form_factory.build()
        active_schedule = replace(active_form.schedule, registration_end=now + timedelta(days=5))
        active_form = active_form.model_copy(update={"schedule": active_schedule})
        created = await create_competition(active_form, api_client)

    response = await api_client.list_preview_competitions()
        
    result = response.assert_status(200).ensure_content()

    result_ids = [item.id for item in result.items]

    assert created.id in result_ids
