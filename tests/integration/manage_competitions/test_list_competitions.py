import asyncio
from collections.abc import Callable
from datetime import datetime

import pytest

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel, CompetitionsList
from dreamteams.application.manage_competitions.list import PAGE_SIZE
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.identifiers import CompetitionId
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import DIFFERENT_USER_ID, USER_ID


async def create_competitions(
    num_competitions: int,
    competition_form_factory: CompetitionFormFactory,
    api_client: ApiClient,
    user_id: str = USER_ID,
) -> list[CompetitionModel]:
    """Create and read competitions."""
    forms = [competition_form_factory.build() for _ in range(num_competitions)]
    with api_client.authenticate(auth_user_id=user_id):
        created_responses = await asyncio.gather(
            *[api_client.create_competition(form.model_dump(mode="json")) for form in forms],
        )
        created = [response.assert_status(200).ensure_content() for response in created_responses]
        read_responses = await asyncio.gather(*[api_client.read_competition(c.competition_id) for c in created])
        return [response.assert_status(200).ensure_content() for response in read_responses]


def create_competitions_list(
    competitions: list[CompetitionModel],
    sort_by: CompetitionSortBy,
    sort_order: SortOrder,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> CompetitionsList:
    """Create ``CompetitionsList`` from ``list[CompetitionModel]`` with sorting applied."""
    sort_key_mapping: dict[CompetitionSortBy, Callable[[CompetitionModel], tuple[datetime | str, CompetitionId]]] = {
        CompetitionSortBy.CREATED_AT: lambda c: (c.created_at, c.id),
        CompetitionSortBy.TITLE: lambda c: (c.title, c.id),
        CompetitionSortBy.REGISTRATION_START: lambda c: (c.schedule.registration_start, c.id),
    }

    sorted_items = sorted(
        competitions,
        key=sort_key_mapping[sort_by],
        reverse=(sort_order == SortOrder.DESC),
    )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = sorted_items[start_idx:end_idx]

    return CompetitionsList(
        items=paginated_items,
        total=len(competitions),
        page=page,
    )


@pytest.fixture(params=[0, 1, 5, 10])
async def created_competitions(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    request: pytest.FixtureRequest,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> list[CompetitionModel]:
    """Create and read competitions."""
    num_competitions = request.param
    return await create_competitions(num_competitions, competition_form_factory, api_client)


async def test_list_competitions_succeeds(
    api_client: ApiClient,
    created_competitions: list[CompetitionModel],
) -> None:
    """Test listing competitions."""
    expected_model = create_competitions_list(
        created_competitions,
        sort_by=CompetitionSortBy.CREATED_AT,
        sort_order=SortOrder.DESC,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


@pytest.mark.parametrize("sort_order", [SortOrder.ASC, SortOrder.DESC])
async def test_list_competitions_sorted_by_created_at(
    api_client: ApiClient,
    created_competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by created_at in different orders."""
    expected_model = create_competitions_list(
        created_competitions,
        sort_by=CompetitionSortBy.CREATED_AT,
        sort_order=sort_order,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=sort_order,
        )

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


@pytest.mark.parametrize("sort_order", [SortOrder.ASC, SortOrder.DESC])
async def test_list_competitions_sorted_by_title(
    api_client: ApiClient,
    created_competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by title in different orders."""
    expected_model = create_competitions_list(
        created_competitions,
        sort_by=CompetitionSortBy.TITLE,
        sort_order=sort_order,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(
            sort_by=CompetitionSortBy.TITLE,
            sort_order=sort_order,
        )

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


@pytest.mark.parametrize("sort_order", [SortOrder.ASC, SortOrder.DESC])
async def test_list_competitions_sorted_by_registration_start(
    api_client: ApiClient,
    created_competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by registration_start in different orders."""
    expected_model = create_competitions_list(
        created_competitions,
        sort_by=CompetitionSortBy.REGISTRATION_START,
        sort_order=sort_order,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(
            sort_by=CompetitionSortBy.REGISTRATION_START,
            sort_order=sort_order,
        )

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_organizers_can_only_see_their_own_competitions(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test that users can only see their own competitions."""
    first_user_competitions = await create_competitions(2, competition_form_factory, api_client, user_id=USER_ID)
    second_user_competitions = await create_competitions(
        3,
        competition_form_factory,
        api_client,
        user_id=DIFFERENT_USER_ID,
    )
    expected_first_user_list = create_competitions_list(
        first_user_competitions,
        sort_by=CompetitionSortBy.CREATED_AT,
        sort_order=SortOrder.DESC,
    )
    expected_second_user_list = create_competitions_list(
        second_user_competitions,
        sort_by=CompetitionSortBy.CREATED_AT,
        sort_order=SortOrder.DESC,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        first_user_list_response = await api_client.list_competitions()
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        second_user_list_response = await api_client.list_competitions()

    first_user_list = first_user_list_response.assert_status(200).ensure_content()
    second_user_list = second_user_list_response.assert_status(200).ensure_content()
    assert first_user_list == expected_first_user_list
    assert second_user_list == expected_second_user_list


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_list_competitions_with_pagination(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001
    page: int,
) -> None:
    """Test listing competitions with pagination."""
    num_competitions = page * PAGE_SIZE
    created = await create_competitions(num_competitions, competition_form_factory, api_client, user_id=USER_ID)
    expected_model = create_competitions_list(
        created,
        sort_by=CompetitionSortBy.CREATED_AT,
        sort_order=SortOrder.DESC,
        page=page,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(page=page)

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_competitions_with_invalid_pagination_fails(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    page: int,
) -> None:
    """Test listing competitions with invalid pagination fails."""
    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(page=page)

    list_response.assert_error(422, "VALIDATION_ERROR")


async def test_list_competitions_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test listing competitions without authentication returns 401."""
    response = await api_client.list_competitions()

    response.assert_error(401, "UNAUTHORIZED")
