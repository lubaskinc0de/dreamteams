from uuid import uuid4

from dreamteams.application.manage_application_form import ApplicationFormInput, CreatedApplicationForm
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID


async def test_competition_owner_can_delete_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
) -> None:
    """Deleting an existing form returns 200."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_application_form(competition.competition_id)

    response.assert_status(200)


async def test_application_form_is_gone_after_deletion(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
) -> None:
    """After a successful delete the form is no longer readable."""
    # Arrange
    with api_client.authenticate(auth_user_id=USER_ID):
        await api_client.delete_application_form(competition.competition_id)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application_form(competition.competition_id)

    # Assert
    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_nonexistent_competition_has_no_form_to_delete(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Deleting a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_application_form(uuid4())

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_competition_without_form_cannot_be_deleted(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Deleting a form from a competition that has none returns APPLICATION_FORM_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_application_form(competition.competition_id)

    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_non_owner_organizer_cannot_delete_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.delete_application_form(competition.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_delete_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    response = await api_client.delete_application_form(competition.competition_id)

    response.assert_error(401, "UNAUTHORIZED")


async def test_deleted_form_can_be_replaced_with_new_one(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
    application_form_input: ApplicationFormInput,
) -> None:
    """After deleting a form, creating a new one for the same competition succeeds."""
    # Arrange
    with api_client.authenticate(auth_user_id=USER_ID):
        await api_client.delete_application_form(competition.competition_id)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            application_form_input.model_dump(mode="json"),
        )

    # Assert
    response.assert_status(200)
