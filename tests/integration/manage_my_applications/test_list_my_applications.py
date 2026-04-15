import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.application.manage_my_applications import ApplicationModel, ApplicationsList
from dreamteams.application.manage_my_applications.list import PAGE_SIZE
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant
from dreamteams.application.submit_application import CreatedApplication
from dreamteams.entities.application.entity import ApplicationStatus
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import PARTICIPANT_USER_ID, USER_ID
from tests.integration.manage_my_applications.helpers import (
    create_competition_and_submit,
    create_my_applications_list,
)


async def test_participant_can_list_own_applications(
    api_client: ApiClient,
    submitted_application: CreatedApplication,
    active_non_autoaccept_competition: CreatedCompetition,
) -> None:
    """Participant who submitted an application sees it in their application list."""
    # Arrange
    application_id = submitted_application.application_id

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationsList(
        items=[
            ApplicationModel(
                id=application_id,
                participant_id=result.items[0].participant_id,
                competition_id=active_non_autoaccept_competition.competition_id,
                domains=result.items[0].domains,
                status=ApplicationStatus.PENDING,
                created_at=result.items[0].created_at,
                form_data=None,
            ),
        ],
        total=1,
        page=1,
    )


async def test_list_my_applications_succeeds(
    api_client: ApiClient,
    my_applications: list[ApplicationModel],
) -> None:
    """All own applications appear in the list regardless of their status."""
    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_my_applications_list(my_applications)


async def test_participant_with_no_applications_gets_empty_list(
    api_client: ApiClient,
    participant: CreatedParticipant,  # noqa: ARG001
) -> None:
    """Participant who has not submitted any applications receives an empty list."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_my_applications()

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationsList(items=[], total=0, page=1)


async def test_unauthenticated_cannot_list_my_applications(
    api_client: ApiClient,
) -> None:
    """Unauthenticated requests to list own applications are rejected with UNAUTHORIZED."""
    # Act
    response = await api_client.list_my_applications()

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_participant_cannot_list_applications(
    api_client: ApiClient,
    competition: CreatedCompetition,  # noqa: ARG001
) -> None:
    """A user without a participant profile is denied with ACCESS_DENIED."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_my_applications()

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


@pytest.mark.parametrize("page", [1, 2])
async def test_list_my_applications_with_pagination(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    submit_application_input_factory: SubmitApplicationInputFactory,
    session: AsyncSession,
    page: int,
) -> None:
    """List own applications returns the correct page and total when there are multiple pages of results."""
    # Arrange — create page * PAGE_SIZE applications from separate competitions
    num_applications = page * PAGE_SIZE
    application_ids = []
    for _ in range(num_applications):
        app_id = await create_competition_and_submit(
            api_client,
            competition_form_factory,
            update_competition_form_factory,
            submit_application_input_factory,
            session,
        )
        application_ids.append(app_id)
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        all_models = [
            (await api_client.read_my_application(app_id)).assert_status(200).ensure_content()
            for app_id in application_ids
        ]

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.list_my_applications(page=page)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == create_my_applications_list(all_models, page=page)


@pytest.mark.parametrize("page", [-2, -1, 0])
async def test_list_my_applications_with_invalid_page_fails(
    api_client: ApiClient,
    participant: CreatedParticipant,  # noqa: ARG001
    page: int,
) -> None:
    """Requesting an invalid page number is rejected with VALIDATION_ERROR."""
    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_my_applications(page=page)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
