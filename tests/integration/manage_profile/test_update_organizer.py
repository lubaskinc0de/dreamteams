from uuid import uuid4

from faker import Faker

from dreamteams.application.manage_profile import OrganizerModel, ProfileModel
from tests.common.factory.organizer import UpdateOrganizerFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_organizer_profile_is_updated(
    api_client: ApiClient,
    gateway: Gateway,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
) -> None:
    """Test that organizer profile fields are persisted after update."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    update_form = update_organizer_form_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        await api_client.update_organizer(update_form.model_dump(mode="json"))
        response = await api_client.view_profile()

    # Assert
    profile = response.assert_status(200).ensure_content()
    assert profile == ProfileModel(
        user_id=organizer.organizer.created.user_id,
        organizer=OrganizerModel(
            id=organizer.organizer.created.organizer_id,
            user_id=organizer.organizer.created.user_id,
            organizer_name=update_form.organizer_name,
            phone_number=organizer.organizer.form.phone_number,
            contact_email=update_form.contact_email,
        ),
        participant=None,
        avatar_url=None,
        is_admin=False,
    )


async def test_update_organizer_with_same_email_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
) -> None:
    """Test that updating organizer with their own existing email does not raise conflict."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    update_form = update_organizer_form_factory.build(contact_email=organizer.organizer.email)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.update_organizer(update_form.model_dump(mode="json"))

    # Assert
    response.assert_status(200)


async def test_update_organizer_fails_if_organizer_name_exceeds_max_length(
    api_client: ApiClient,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test that organizer_name longer than 70 characters is rejected with 422."""
    data = update_organizer_form_factory.build().model_copy(update={"organizer_name": "a" * 71})

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_organizer(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_organizer_fails_if_contact_email_is_malformed(
    api_client: ApiClient,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test that a malformed contact email is rejected with 422."""
    data = update_organizer_form_factory.build().model_copy(
        update={"contact_email": "not-an-email"},
    )

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_organizer(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_organizer_fails_if_email_already_taken(
    api_client: ApiClient,
    gateway: Gateway,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
) -> None:
    """Test that updating organizer email to one already in use returns 409."""
    # Arrange
    first = await gateway.organizer.create_with_admin(gateway.admin)
    second = await gateway.organizer.create(admin_auth_id=first.admin.auth_id)
    update_form = update_organizer_form_factory.build(contact_email=first.organizer.email)

    # Act
    with api_client.authenticate(auth_user_id=second.auth_id):
        response = await api_client.update_organizer(update_form.model_dump(mode="json"))

    # Assert
    response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_update_organizer_fails_if_user_has_no_organizer_role(
    api_client: ApiClient,
    gateway: Gateway,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
) -> None:
    """Test that updating organizer profile returns 404 when user has no organizer role."""
    # Arrange
    participant = await gateway.participant.create()
    update_form = update_organizer_form_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_organizer(update_form.model_dump(mode="json"))

    # Assert
    response.assert_error(404, "ORGANIZER_NOT_FOUND")


async def test_update_organizer_fails_if_unauthorized(
    api_client: ApiClient,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
) -> None:
    """Test that updating organizer profile returns 401 when not authenticated."""
    update_form = update_organizer_form_factory.build()

    response = await api_client.update_organizer(update_form.model_dump(mode="json"))

    response.assert_error(401, "UNAUTHORIZED")


async def test_update_organizer_fails_if_user_not_found(
    api_client: ApiClient,
    update_organizer_form_factory: UpdateOrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test that updating organizer profile returns 401 when auth ID is not linked to any user."""
    # Arrange
    update_form = update_organizer_form_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_organizer(update_form.model_dump(mode="json"))

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
