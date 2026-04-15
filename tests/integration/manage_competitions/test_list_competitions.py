import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.manage_competitions.list import PAGE_SIZE
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import create_competition, create_competitions
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID
from tests.integration.competition_helpers import change_archived_state, create_competitions_list, make_all_active


async def test_list_competitions_succeeds(
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> None:
    """Test listing competitions."""
    expected_model = create_competitions_list(
        competitions,
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
    competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by created_at in different orders."""
    expected_model = create_competitions_list(
        competitions,
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
    competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by title in different orders."""
    expected_model = create_competitions_list(
        competitions,
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
    competitions: list[CompetitionModel],
    sort_order: SortOrder,
) -> None:
    """Test sorting competitions by registration_start in different orders."""
    expected_model = create_competitions_list(
        competitions,
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


@pytest.mark.parametrize("sort_order", [SortOrder.ASC, SortOrder.DESC])
@pytest.mark.parametrize("is_archived", [True, False])
async def test_list_competitions_filtered_by_is_archived(
    api_client: ApiClient,
    competitions: list[CompetitionModel],
    sort_order: SortOrder,
    competition_form_factory: CompetitionFormFactory,
    session: AsyncSession,
    is_archived: bool,  # noqa: FBT001
) -> None:
    """Test filtering competitions by is archived in different orders."""
    archived_competitions = await change_archived_state(session, api_client, competitions, is_archived=True)
    active_competitions = await make_all_active(
        session,
        api_client,
        await create_competitions(3, competition_form_factory, api_client),
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=sort_order,
            is_archived=is_archived,
        )

    result = list_response.assert_status(200).ensure_content()
    assert (
        result
        == create_competitions_list(
            archived_competitions,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=sort_order,
        )
        if is_archived is True
        else create_competitions_list(
            active_competitions,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=sort_order,
        )
    )


@pytest.mark.parametrize(
    ("search_query", "competitions", "expected_competitions_titles"),
    [
        # Basic exact matches
        (
            "Foo",
            [
                {"title": "Foo", "description": "Foo"},
                {"title": "Bar", "description": "Bar"},
                {"title": "Fo", "description": "Fo"},
            ],
            ["Foo", "Fo"],  # "Fo" is similar to "Foo"
        ),
        (
            "Bar",
            [
                {"title": "Foo", "description": "Foo"},
                {"title": "Bar", "description": "Bar"},
                {"title": "Fo", "description": "Fo"},
            ],
            ["Bar"],
        ),
        # Partial word matches
        (
            "rogram",
            [
                {"title": "Programming Contest", "description": "Coding competition"},
                {"title": "Progressive Marathon", "description": "Running event"},
                {"title": "Game Tournament", "description": "Gaming competition"},
            ],
            ["Programming Contest"],
        ),
        # Case insensitive search
        (
            "python",
            [
                {"title": "Python Hackathon", "description": "Coding in Python"},
                {"title": "PYTHON Workshop", "description": "Learn programming"},
                {"title": "Java Competition", "description": "Java coding"},
            ],
            ["Python Hackathon", "PYTHON Workshop"],
        ),
        # Multiple words
        (
            "code competition",
            [
                {"title": "Coding Challenge", "description": "Competition for programmers"},
                {"title": "Code Review Contest", "description": "Review competition"},
                {"title": "Design Competition", "description": "No code here"},
            ],
            ["Design Competition", "Code Review Contest", "Coding Challenge"],
        ),
        # Short search terms
        (
            "AI",
            [
                {"title": "AI Competition", "description": "Artificial intelligence"},
                {"title": "AIML Challenge", "description": "AI and ML"},
                {"title": "Programming", "description": "General programming"},
            ],
            ["AI Competition"],
        ),
        # No matches
        (
            "XYZ",
            [
                {"title": "ABC Competition", "description": "Test event"},
                {"title": "DEF Tournament", "description": "Another test"},
                {"title": "GHI Challenge", "description": "Test challenge"},
            ],
            [],  # No similarity
        ),
        # Verify result ordering
        (
            "competition",
            [
                {"title": "Competition", "description": "Just competition"},
                {"title": "My Competition", "description": "My competition"},
                {"title": "Computer science", "description": "I love my computer"},
            ],
            [
                "Competition",
                "My Competition",
                "Computer science",
            ],
        ),
        # Search with dash
        (
            "data-science",
            [
                {"title": "Data Science Hackathon", "description": "Data science competition"},
                {"title": "Данные", "description": "Analyze"},
                {"title": "Science Fair", "description": "General science"},
            ],
            [
                "Science Fair",
                "Data Science Hackathon",
            ],
        ),
    ],
)
async def test_search_competitions(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001,
    session: AsyncSession,
    search_query: str,
    competitions: list[dict[str, str]],
    expected_competitions_titles: list[str],
) -> None:
    """Test searching competitions."""
    with api_client.authenticate(auth_user_id=USER_ID):
        created_competitions = await asyncio.gather(
            *[
                create_competition(
                    competition_form_factory.build(factory_use_construct=False, **competition_data),
                    api_client,
                )
                for competition_data in competitions
            ],
        )
    # make some competitions active to ensure that they are searched too
    await make_all_active(
        session,
        api_client,
        created_competitions[: len(created_competitions) // 2],
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        list_response = await api_client.list_competitions(search=search_query)

    actual_titles = [competition.title for competition in list_response.assert_status(200).ensure_content().items]
    assert actual_titles == expected_competitions_titles


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
