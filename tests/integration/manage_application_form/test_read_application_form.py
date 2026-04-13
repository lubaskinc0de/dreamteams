from uuid import uuid4

from dreamteams.application.manage_application_form import ApplicationFormModel, CreatedApplicationForm
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID


async def test_competition_owner_can_read_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,
) -> None:
    """Organizer receives the full form definition when reading their competition's form."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application_form(competition.competition_id)

    result = response.assert_status(200).ensure_content()
    assert result == ApplicationFormModel(
        id=created_application_form.application_form_id,
        competition_id=competition.competition_id,
        created_at=result.created_at,
        fields=result.fields,
    )


async def test_nonexistent_competition_has_no_application_form(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Reading a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application_form(uuid4())

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_competition_without_form_returns_not_found(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """Reading a form for a competition that has none returns APPLICATION_FORM_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_application_form(competition.competition_id)

    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_non_owner_organizer_cannot_read_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.read_application_form(competition.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_read_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    response = await api_client.read_application_form(competition.competition_id)

    response.assert_error(401, "UNAUTHORIZED")
