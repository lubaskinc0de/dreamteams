import pytest

from dreamteams.application.common.gateway.competition import CompetitionSortBy, ExploreSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.submit_application.list_competitions import PAGE_SIZE, ExploreCompetitionsList
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competitions_list_to_explore_list, create_competitions_list
from tests.integration.helpers.facade import Gateway

# --- Access control ---


async def test_unauthenticated_cannot_explore_competitions(api_client: ApiClient) -> None:
    """Unauthenticated requests to /competitions/explore are rejected with UNAUTHORIZED."""
    # Act
    response = await api_client.explore_competitions()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_participant_is_rejected_with_access_denied(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A user without a participant profile (only an organizer) is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


# --- Eligibility filters ---


async def test_participant_sees_empty_list_when_no_competitions_exist(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A participant with no available competitions receives an empty list."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


async def test_archived_competitions_are_hidden(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competitions whose ``is_archived`` flag is True do not appear in explore results."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    await gateway.competition.create_many(owner.organizer.auth_id, 3)  # archived by default

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


async def test_competitions_with_closed_registration_are_hidden(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competitions whose registration window has already ended are not returned."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    competitions = await gateway.competition.create_many(owner.organizer.auth_id, 3)
    await gateway.competition.make_all_passed(competitions, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


async def test_already_applied_competitions_are_hidden(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competitions to which the participant has already submitted an application are hidden."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


async def test_competitions_with_mismatched_participant_type_are_hidden(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A competition requiring a specific participant_type is hidden from participants of a different type."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create(participant_type=ParticipantType.STUDENT)
    await gateway.competition.create_active(
        owner.organizer.auth_id,
        participant_type=ParticipantType.SCHOOLCHILD,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


@pytest.mark.parametrize("max_participants", [1, 5])
async def test_full_capacity_competitions_are_hidden(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    max_participants: int,
) -> None:
    """Competitions whose accepted count has reached ``participant_limits.max`` are hidden."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(
        owner.organizer.auth_id,
        auto_accept=True,
        max_participants=max_participants,
    )
    submit_input = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)
    await gateway.application.create_for_competition(
        max_participants,
        comp.created.competition_id,
        submit_input,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ExploreCompetitionsList(items=[], total=0, page=1)


# --- Sorting ---


@pytest.mark.parametrize(
    "member_counts",
    [
        [0, 2, 5],
        [1, 3, 10],
    ],
)
async def test_default_sort_is_most_popular_by_accepted_count(
    api_client: ApiClient,
    gateway: Gateway,
    member_counts: list[int],
) -> None:
    """Default sort orders competitions by descending number of accepted applications."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    competitions = await gateway.application.create_active_competitions_with_accepted_members(
        owner.organizer.auth_id,
        member_counts,
    )
    read_models = [
        await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id) for comp in competitions
    ]
    sorted_by_popularity = sorted(read_models, key=lambda c: c.members_count, reverse=True)
    expected = competitions_list_to_explore_list(
        create_competitions_list(sorted_by_popularity, sort_by=None, sort_order=None),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    assert response.assert_status(200).ensure_content() == expected


async def test_newest_sort_orders_by_created_at_desc(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """``sort_by=newest`` orders competitions from newest to oldest creation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    active = await gateway.competition.create_many_active(owner.organizer.auth_id, 3)
    expected = competitions_list_to_explore_list(
        create_competitions_list(active, sort_by=CompetitionSortBy.CREATED_AT, sort_order=SortOrder.DESC),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(sort_by=ExploreSortBy.NEWEST)

    # Assert
    assert response.assert_status(200).ensure_content() == expected


# --- Search ---


@pytest.mark.parametrize(
    ("search_query", "competitions", "expected_competitions_titles"),
    [
        (
            "Foo",
            [
                {"title": "Foo", "description": "Foo"},
                {"title": "Bar", "description": "Bar"},
                {"title": "Foos", "description": "Foos"},
            ],
            ["Foo", "Foos"],
        ),
        (
            "rogram",
            [
                {"title": "Programming Contest", "description": "Coding competition"},
                {"title": "Progressive Marathon", "description": "Running event"},
                {"title": "Game Tournament", "description": "Gaming competition"},
            ],
            ["Programming Contest"],
        ),
        (
            "python",
            [
                {"title": "Python Hackathon", "description": "Coding in Python"},
                {"title": "PYTHON Workshop", "description": "Learn programming"},
                {"title": "Java Competition", "description": "Java coding"},
            ],
            ["Python Hackathon", "PYTHON Workshop"],
        ),
        (
            "XYZ",
            [
                {"title": "ABC Competition", "description": "Test event"},
                {"title": "DEF Tournament", "description": "Another test"},
            ],
            [],
        ),
    ],
)
async def test_search_filters_by_title_similarity(
    api_client: ApiClient,
    gateway: Gateway,
    competition_form_factory: CompetitionFormFactory,
    search_query: str,
    competitions: list[dict[str, str]],
    expected_competitions_titles: list[str],
) -> None:
    """Providing a search query returns only competitions whose title is similar."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    forms = [
        competition_form_factory.build(
            factory_use_construct=False,
            participant_type=ParticipantType.ANY,
            **data,
        )
        for data in competitions
    ]
    created = await gateway.competition.create_many_from_form(owner.organizer.auth_id, forms)
    await gateway.competition.make_all_active(created, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(search=search_query, sort_by=ExploreSortBy.NEWEST)

    # Assert
    titles = [item.title for item in response.assert_status(200).ensure_content().items]
    assert sorted(titles) == sorted(expected_competitions_titles)


# --- Structured filters ---


@pytest.mark.parametrize(
    ("comp_min", "comp_max", "query_min", "query_max", "expected_included"),
    [
        (3, 5, 2, 4, True),
        (3, 5, 5, 10, True),
        (3, 5, 6, 10, False),
        (3, 5, None, 2, False),
        (3, 5, 1, None, True),
        (4, 8, 1, 3, False),
        (4, 8, 8, 12, True),
    ],
)
async def test_team_size_range_overlap_filter(
    api_client: ApiClient,
    gateway: Gateway,
    competition_form_factory: CompetitionFormFactory,
    comp_min: int,
    comp_max: int,
    query_min: int | None,
    query_max: int | None,
    *,
    expected_included: bool,
) -> None:
    """Team size filter returns a competition only when its team-size range overlaps the query range."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    form = competition_form_factory.build(participant_type=ParticipantType.ANY)
    form.team_size = TeamSizeRange(min=comp_min, max=comp_max)
    competition = await gateway.competition.create_from_form(owner.organizer.auth_id, form)
    [active] = await gateway.competition.make_all_active([competition], owner.organizer.auth_id)
    expected_items = (
        competitions_list_to_explore_list(
            create_competitions_list([active], sort_by=CompetitionSortBy.CREATED_AT, sort_order=SortOrder.DESC),
            owner.organizer.form,
            owner.organizer.created.organizer_id,
        ).items
        if expected_included
        else []
    )
    expected = ExploreCompetitionsList(items=expected_items, total=len(expected_items), page=1)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(
            min_team_size=query_min,
            max_team_size=query_max,
        )

    # Assert
    assert response.assert_status(200).ensure_content() == expected


@pytest.mark.parametrize("requested_auto_accept", [True, False])
async def test_auto_accept_filter_returns_only_matching_competitions(
    api_client: ApiClient,
    gateway: Gateway,
    *,
    requested_auto_accept: bool,
) -> None:
    """Filtering by ``auto_accept`` returns competitions whose flag matches the query."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    auto = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=True)
    manual = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    expected_id = auto.created.competition_id if requested_auto_accept else manual.created.competition_id
    expected_model = await gateway.competition.read(expected_id, owner.organizer.auth_id)
    expected = competitions_list_to_explore_list(
        create_competitions_list(
            [expected_model],
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(auto_accept=requested_auto_accept)

    # Assert
    assert response.assert_status(200).ensure_content() == expected


@pytest.mark.parametrize(
    ("comp_a_domains", "comp_b_domains", "query_domains", "expected_match"),
    [
        ([Domain.BACKEND], [Domain.FRONTEND], [Domain.BACKEND], "a"),
        ([Domain.BACKEND, Domain.AI], [Domain.FRONTEND], [Domain.AI], "a"),
        ([Domain.BACKEND], [Domain.FRONTEND], [Domain.FRONTEND], "b"),
        ([Domain.BACKEND], [Domain.FRONTEND], [Domain.AI], "none"),
        ([Domain.BACKEND], [Domain.FRONTEND], [Domain.BACKEND, Domain.FRONTEND], "both"),
    ],
)
async def test_domains_filter_returns_competitions_with_overlapping_domains(
    api_client: ApiClient,
    gateway: Gateway,
    comp_a_domains: list[Domain],
    comp_b_domains: list[Domain],
    query_domains: list[Domain],
    expected_match: str,
) -> None:
    """``domains=[...]`` returns only competitions whose ``domains`` overlap with the query."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp_a = await gateway.competition.create_active(owner.organizer.auth_id, domains=comp_a_domains)
    comp_b = await gateway.competition.create_active(owner.organizer.auth_id, domains=comp_b_domains)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(domains=query_domains)

    # Assert
    result = response.assert_status(200).ensure_content()
    returned_ids = {item.id for item in result.items}
    expected_ids = {
        "a": {comp_a.created.competition_id},
        "b": {comp_b.created.competition_id},
        "both": {comp_a.created.competition_id, comp_b.created.competition_id},
        "none": set(),
    }[expected_match]
    assert returned_ids == expected_ids


# --- Pagination + response shape ---


@pytest.mark.parametrize("page", [1, 2])
async def test_pagination_respects_page_size(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Explore list returns pages of ``PAGE_SIZE`` rows and reports the correct total."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    active = await gateway.competition.create_many_active(owner.organizer.auth_id, page * PAGE_SIZE)
    all_explore = competitions_list_to_explore_list(
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
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(page=page, sort_by=ExploreSortBy.NEWEST)

    # Assert
    assert response.assert_status(200).ensure_content() == ExploreCompetitionsList(
        items=all_explore.items[(page - 1) * PAGE_SIZE : page * PAGE_SIZE],
        total=all_explore.total,
        page=page,
    )


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_explore_with_invalid_pagination_fails(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Non-positive page numbers are rejected with VALIDATION_ERROR."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions(page=page)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize("accepted_count", [1, 3, 5])
async def test_members_count_reflects_accepted_applications(
    api_client: ApiClient,
    gateway: Gateway,
    accepted_count: int,
) -> None:
    """``members_count`` on each row equals the number of ACCEPTED applications at query time."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    [comp] = await gateway.application.create_active_competitions_with_accepted_members(
        owner.organizer.auth_id,
        [accepted_count],
    )
    comp_model = await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id)
    expected = competitions_list_to_explore_list(
        create_competitions_list(
            [comp_model],
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
        owner.organizer.form,
        owner.organizer.created.organizer_id,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.explore_competitions()

    # Assert
    assert response.assert_status(200).ensure_content() == expected
