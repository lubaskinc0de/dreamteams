from uuid import uuid4

import pytest

from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.input_limits import MAX_PAGE
from dreamteams.application.view_submitted_applications.list_applications import MAX_PAGE_SIZE, PAGE_SIZE
from dreamteams.entities.application.entity import ApplicationStatus
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.submitted_application_lists import create_applications_list


@pytest.mark.parametrize("num_applications", [0, 1, 5, 10])
async def test_list_applications_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    num_applications: int,
) -> None:
    """All submitted applications appear in the list regardless of their status."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    submit_input = submit_application_input_factory.build(
        track=CompetitionTrackForm(name=comp.form.tracks[0].name),
        form_data=None,
    )
    submitted_ids = await gateway.application.create_for_competition(
        num_applications,
        comp.created.competition_id,
        submit_input,
    )
    all_models = await gateway.application.create_mixed(submitted_ids, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(comp.created.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models)


async def test_organizer_sees_empty_list_when_no_applications(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competition with no submissions returns an empty application list."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(comp.created.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list([])


async def test_list_applications_fails_if_user_has_no_organizer_role(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Listing applications fails when user has no organizer role."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
        )

    response.assert_error(404, "ORGANIZER_NOT_FOUND")


async def test_unauthenticated_cannot_list_applications_by_competition(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests to list applications are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    response = await api_client.list_applications_by_competition(comp.created.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_list_applications(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.list_applications_by_competition(comp.created.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_listing_applications_for_nonexistent_competition_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Listing applications for a competition that does not exist is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(nonexistent_id)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


@pytest.mark.parametrize("page", [1, 2])
async def test_list_applications_with_pagination(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    page: int,
) -> None:
    """Applications list returns the correct page and total when there are multiple pages of results."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    num_applications = page * PAGE_SIZE
    submit_input = submit_application_input_factory.build(
        track=CompetitionTrackForm(name=comp.form.tracks[0].name),
        form_data=None,
    )
    submitted_ids = await gateway.application.create_for_competition(
        num_applications,
        comp.created.competition_id,
        submit_input,
    )
    all_models = [
        await gateway.application.read_as_organizer(app_id, owner.organizer.auth_id) for app_id in submitted_ids
    ]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            page=page,
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models, page=page)


@pytest.mark.parametrize(("page", "page_size", "num_applications"), [(2, 4, 9)])
async def test_list_applications_respects_page_size(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    page: int,
    page_size: int,
    num_applications: int,
) -> None:
    """Applications list uses the caller-provided page size."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    submit_input = submit_application_input_factory.build(
        track=CompetitionTrackForm(name=comp.form.tracks[0].name),
        form_data=None,
    )
    submitted_ids = await gateway.application.create_for_competition(
        num_applications,
        comp.created.competition_id,
        submit_input,
    )
    all_models = [
        await gateway.application.read_as_organizer(app_id, owner.organizer.auth_id) for app_id in submitted_ids
    ]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            page=page,
            page_size=page_size,
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models, page=page, page_size=page_size)


@pytest.mark.parametrize(
    "status",
    [ApplicationStatus.PENDING, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
)
async def test_list_applications_filters_by_status(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    status: ApplicationStatus,
) -> None:
    """Filtering by status returns only applications in that status."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    submit_input = submit_application_input_factory.build(
        track=CompetitionTrackForm(name=comp.form.tracks[0].name),
        form_data=None,
    )
    submitted_ids = await gateway.application.create_for_competition(
        6,
        comp.created.competition_id,
        submit_input,
    )
    all_models = await gateway.application.create_mixed(submitted_ids, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            status=status,
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models, status=status)


@pytest.mark.parametrize("sort_order", [SortOrder.ASC, SortOrder.DESC])
async def test_list_applications_respects_sort_order(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    sort_order: SortOrder,
) -> None:
    """Results are ordered by created_at in the requested direction."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    submit_input = submit_application_input_factory.build(
        track=CompetitionTrackForm(name=comp.form.tracks[0].name),
        form_data=None,
    )
    submitted_ids = await gateway.application.create_for_competition(
        3,
        comp.created.competition_id,
        submit_input,
    )
    all_models = [
        await gateway.application.read_as_organizer(app_id, owner.organizer.auth_id) for app_id in submitted_ids
    ]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            sort_order=sort_order,
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models, sort_order=sort_order)


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_applications_with_invalid_page_fails(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Requesting an invalid page number is rejected with VALIDATION_ERROR."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            page=page,
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_list_applications_rejects_too_large_page(api_client: ApiClient, gateway: Gateway) -> None:
    """Submitted application list rejects page numbers above the configured cap."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            page=MAX_PAGE + 1,
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize("page_size", [-1, 0, MAX_PAGE_SIZE + 1])
async def test_list_applications_with_invalid_page_size_fails(
    api_client: ApiClient,
    gateway: Gateway,
    page_size: int,
) -> None:
    """Requesting an invalid page size is rejected with VALIDATION_ERROR."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.list_applications_by_competition(
            comp.created.competition_id,
            page_size=page_size,
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
