import asyncio

import pytest

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.manage_competitions.list import PAGE_SIZE
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import DIFFERENT_USER_ID, USER_ID, create_competition, create_competitions
from tests.integration.manage_competitions.helpers import create_competitions_list, update_competition


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
    update_competition_form_factory: UpdateCompetitionFormFactory,
    is_archived: bool,  # noqa: FBT001
) -> None:
    """Test filtering competitions by is archived in different orders."""
    update_data = update_competition_form_factory.build().model_copy(update={"is_archived": False})
    active_competition = await create_competitions(1, competition_form_factory, api_client)
    await update_competition(active_competition[0].id, data=update_data, api_client=api_client)

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
            competitions,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=sort_order,
        )
        if is_archived is True
        else create_competitions_list(
            active_competition,
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
        # Search in description
        (
            "description",
            [
                {"title": "Competition", "description": "This is an interesting description"},
                {"title": "Tournament", "description": "Another description"},
                {"title": "Challenge", "description": "No match here"},
            ],
            ["Tournament", "Competition"],  # "Tournament" might rank higher
        ),
        # Combined search
        (
            "championship",
            [
                {"title": "Football Championship", "description": "Annual tournament"},
                {"title": "Basketball", "description": "Championship league"},
                {"title": "Tennis", "description": "Tournament"},
            ],
            ["Basketball", "Football Championship"],  # "Championship" in description might rank higher
        ),
        # Partial word matches
        (
            "rogram",
            [
                {"title": "Programming Contest", "description": "Coding competition"},
                {"title": "Progressive Marathon", "description": "Running event"},
                {"title": "Game Tournament", "description": "Gaming competition"},
            ],
            [],  # "rogram" is too different from "Programming" with high threshold
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
            ["Code Review Contest", "Design Competition", "Coding Challenge"],
        ),
        # Short search terms
        (
            "AI",
            [
                {"title": "AI Competition", "description": "Artificial intelligence"},
                {"title": "AIML Challenge", "description": "AI and ML"},
                {"title": "Programming", "description": "General programming"},
            ],
            [],
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
            ["My Competition", "Competition"],
        ),
        # Search with dash
        (
            "data-science",
            [
                {"title": "Data Science Hackathon", "description": "Data science competition"},
                {"title": "Данные", "description": "Analyze"},
                {"title": "Science Fair", "description": "General science"},
            ],
            ["Data Science Hackathon", "Science Fair"],
        ),
    ],
)
async def test_search_competitions(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    organizer: CreatedOrganizer,  # noqa: ARG001,
    search_query: str,
    competitions: list[dict[str, str]],
    expected_competitions_titles: list[str],
) -> None:
    """Test searching competitions."""
    with api_client.authenticate(auth_user_id=USER_ID):
        await asyncio.gather(
            *[
                create_competition(
                    competition_form_factory.build(factory_use_construct=False, **competition_data),
                    api_client,
                )
                for competition_data in competitions
            ],
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
