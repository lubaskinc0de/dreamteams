from uuid import uuid4

from dreamteams.application.manage_application_form import ApplicationFormInput, CreatedApplicationForm
from dreamteams.application.manage_application_form.create_application_form import FieldChoiceForm, FieldForm
from dreamteams.entities.application_form.vo.field import FieldType
from tests.common.factory.application_form import ApplicationFormInputFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_competition_owner_can_attach_application_form(
    api_client: ApiClient,
    gateway: Gateway,
    application_form_input_factory: ApplicationFormInputFactory,
) -> None:
    """Organizer receives a valid application_form_id when creating a form for their competition."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    form_input = application_form_input_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(
            comp.created.competition_id,
            form_input.model_dump(mode="json"),
        )

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplicationForm(application_form_id=result.application_form_id)


async def test_nonexistent_competition_cannot_have_application_form(
    api_client: ApiClient,
    gateway: Gateway,
    application_form_input_factory: ApplicationFormInputFactory,
) -> None:
    """Creating a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    form_input = application_form_input_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(
            uuid4(),
            form_input.model_dump(mode="json"),
        )

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_competition_can_only_have_one_application_form(
    api_client: ApiClient,
    gateway: Gateway,
    application_form_input_factory: ApplicationFormInputFactory,
) -> None:
    """A competition with an existing form rejects a second creation with APPLICATION_FORM_ALREADY_EXISTS."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    form_input = application_form_input_factory.build()
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id, form_input)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(
            comp.created.competition_id,
            form_input.model_dump(mode="json"),
        )

    # Assert
    response.assert_error(409, "APPLICATION_FORM_ALREADY_EXISTS")


async def test_non_owner_organizer_cannot_attach_application_form(
    api_client: ApiClient,
    gateway: Gateway,
    application_form_input_factory: ApplicationFormInputFactory,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    form_input = application_form_input_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.create_application_form(
            comp.created.competition_id,
            form_input.model_dump(mode="json"),
        )

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_create_application_form(
    api_client: ApiClient,
    gateway: Gateway,
    application_form_input_factory: ApplicationFormInputFactory,
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    form_input = application_form_input_factory.build()

    # Act
    response = await api_client.create_application_form(
        comp.created.competition_id,
        form_input.model_dump(mode="json"),
    )

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_application_form_requires_at_least_one_field(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A form submitted with no fields is rejected with INVALID_APPLICATION_FORM_DATA."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(
            comp.created.competition_id,
            {"fields": []},
        )

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_application_form_field_names_must_be_unique(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A form with duplicate field names is rejected with INVALID_APPLICATION_FORM_DATA."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = {
        "fields": [
            {"name": "bio", "type": "string", "required": True, "choices": None},
            {"name": "bio", "type": "string", "required": False, "choices": None},
        ],
    }

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(comp.created.competition_id, data)

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_select_field_without_choices_is_invalid(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A SELECT field with no choices is rejected with INVALID_APPLICATION_FORM_DATA."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = {
        "fields": [
            {"name": "size", "type": "select", "required": True, "choices": None},
        ],
    }

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(comp.created.competition_id, data)

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_string_field_with_choices_is_invalid(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A STRING field that carries choices is rejected with INVALID_APPLICATION_FORM_DATA."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = {
        "fields": [
            {
                "name": "bio",
                "type": "string",
                "required": True,
                "choices": [{"value": "x"}],
            },
        ],
    }

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(comp.created.competition_id, data)

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_FORM_DATA")


async def test_select_field_with_valid_choices_is_accepted(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """A form containing a SELECT field with at least one choice is accepted."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = ApplicationFormInput(
        fields=[
            FieldForm(
                name="role",
                type=FieldType.SELECT,
                required=True,
                choices=[
                    FieldChoiceForm(value="dev"),
                    FieldChoiceForm(value="des"),
                ],
            ),
        ],
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_application_form(
            comp.created.competition_id,
            data.model_dump(mode="json"),
        )

    # Assert
    response.assert_status(200)
