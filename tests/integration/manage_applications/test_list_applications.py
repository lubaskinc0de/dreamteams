from uuid import uuid4

import pytest
from faker import Faker

from dreamteams.application.manage_applications.list import PAGE_SIZE
from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.publish_competition import CompetitionForm, CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID
from tests.integration.manage_applications.helpers import (
    create_applications_for_competition,
    create_applications_list,
)


async def test_list_applications_succeeds(
    api_client: ApiClient,
    active_non_autoaccept_competition: CreatedCompetition,
    applications: list[ApplicationModel],
) -> None:
    """All submitted applications appear in the list regardless of their status."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_applications_by_competition(active_non_autoaccept_competition.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(applications)


async def test_organizer_sees_empty_list_when_no_applications(
    api_client: ApiClient,
    non_autoaccept_competition: CreatedCompetition,
) -> None:
    """Competition with no submissions returns an empty application list."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_applications_by_competition(non_autoaccept_competition.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list([])


async def test_unauthenticated_cannot_list_applications_by_competition(
    api_client: ApiClient,
    non_autoaccept_competition: CreatedCompetition,
) -> None:
    """Unauthenticated requests to list applications are rejected with UNAUTHORIZED."""
    # Act
    response = await api_client.list_applications_by_competition(non_autoaccept_competition.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_list_applications(
    api_client: ApiClient,
    non_autoaccept_competition: CreatedCompetition,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Act
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.list_applications_by_competition(non_autoaccept_competition.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_listing_applications_for_nonexistent_competition_fails(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Listing applications for a competition that does not exist is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_applications_by_competition(nonexistent_id)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


@pytest.mark.parametrize("page", [1, 2])
async def test_list_applications_with_pagination(
    api_client: ApiClient,
    active_non_autoaccept_competition: CreatedCompetition,
    competition_form: CompetitionForm,
    submit_application_input_factory: SubmitApplicationInputFactory,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
    page: int,
) -> None:
    """Applications list returns the correct page and total when there are multiple pages of results."""
    # Arrange — create page * PAGE_SIZE applications so all pages are populated
    num_applications = page * PAGE_SIZE
    submit_input = submit_application_input_factory.build(
        domains=[competition_form.domains[0]],
        form_data=None,
    )
    submitted_ids = await create_applications_for_competition(
        num_applications,
        api_client,
        active_non_autoaccept_competition.competition_id,
        submit_input,
        participant_form_factory,
        faker,
    )
    with api_client.authenticate(auth_user_id=USER_ID):
        all_models = [
            (await api_client.read_application(app_id)).assert_status(200).ensure_content() for app_id in submitted_ids
        ]

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_applications_by_competition(
            active_non_autoaccept_competition.competition_id,
            page=page,
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_applications_list(all_models, page=page)


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_applications_with_invalid_page_fails(
    api_client: ApiClient,
    non_autoaccept_competition: CreatedCompetition,
    page: int,
) -> None:
    """Requesting an invalid page number is rejected with VALIDATION_ERROR."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_applications_by_competition(
            non_autoaccept_competition.competition_id,
            page=page,
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
