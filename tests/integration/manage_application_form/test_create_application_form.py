from uuid import uuid4

from dreamteams.application.manage_application_form import ApplicationFormInput, CreatedApplicationForm
from dreamteams.application.manage_application_form.create import FieldChoiceForm, FieldForm
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.application_form.vo.field import FieldType
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID


async def test_competition_owner_can_attach_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    application_form_input: ApplicationFormInput,
) -> None:
    """Organizer receives a valid application_form_id when creating a form for their competition."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            application_form_input.model_dump(mode="json"),
        )

    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplicationForm(application_form_id=result.application_form_id)


async def test_nonexistent_competition_cannot_have_application_form(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    application_form_input: ApplicationFormInput,
) -> None:
    """Creating a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            uuid4(),
            application_form_input.model_dump(mode="json"),
        )

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_competition_can_only_have_one_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    created_application_form: CreatedApplicationForm,  # noqa: ARG001
    application_form_input: ApplicationFormInput,
) -> None:
    """A competition with an existing form rejects a second creation with APPLICATION_FORM_ALREADY_EXISTS."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            application_form_input.model_dump(mode="json"),
        )

    response.assert_error(409, "APPLICATION_FORM_ALREADY_EXISTS")


async def test_non_owner_organizer_cannot_attach_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
    application_form_input: ApplicationFormInput,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            application_form_input.model_dump(mode="json"),
        )

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_create_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    application_form_input: ApplicationFormInput,
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    response = await api_client.create_application_form(
        competition.competition_id,
        application_form_input.model_dump(mode="json"),
    )

    response.assert_error(401, "UNAUTHORIZED")


async def test_application_form_requires_at_least_one_field(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """A form submitted with no fields is rejected with INVALID_APPLICATION_FORM_DATA."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            {"fields": []},
        )

    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_application_form_field_names_must_be_unique(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """A form with duplicate field names is rejected with INVALID_APPLICATION_FORM_DATA."""
    data = {
        "fields": [
            {"name": "bio", "label": "Bio", "type": "string", "required": True, "choices": None},
            {"name": "bio", "label": "Biography", "type": "string", "required": False, "choices": None},
        ],
    }

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(competition.competition_id, data)

    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_select_field_without_choices_is_invalid(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """A SELECT field with no choices is rejected with INVALID_APPLICATION_FORM_DATA."""
    data = {
        "fields": [
            {"name": "size", "label": "T-shirt size", "type": "select", "required": True, "choices": None},
        ],
    }

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(competition.competition_id, data)

    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_string_field_with_choices_is_invalid(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """A STRING field that carries choices is rejected with INVALID_APPLICATION_FORM_DATA."""
    data = {
        "fields": [
            {
                "name": "bio",
                "label": "Bio",
                "type": "string",
                "required": True,
                "choices": [{"value": "x", "label": "X"}],
            },
        ],
    }

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(competition.competition_id, data)

    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_select_field_with_valid_choices_is_accepted(
    api_client: ApiClient,
    competition: CreatedCompetition,
) -> None:
    """A form containing a SELECT field with at least one choice is accepted."""
    data = ApplicationFormInput(
        fields=[
            FieldForm(
                name="role",
                label="Your role",
                type=FieldType.SELECT,
                required=True,
                choices=[
                    FieldChoiceForm(value="dev", label="Developer"),
                    FieldChoiceForm(value="des", label="Designer"),
                ],
            ),
        ],
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            data.model_dump(mode="json"),
        )

    response.assert_status(200)
