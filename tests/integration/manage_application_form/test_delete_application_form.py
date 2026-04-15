from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_competition_owner_can_delete_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Deleting an existing form returns 200."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_application_form(comp.created.competition_id)

    # Assert
    response.assert_status(200)


async def test_application_form_is_gone_after_deletion(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """After a successful delete the form is no longer readable."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        (await api_client.delete_application_form(comp.created.competition_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_application_form(comp.created.competition_id)

    # Assert
    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_nonexistent_competition_has_no_form_to_delete(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Deleting a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_application_form(uuid4())

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_competition_without_form_cannot_be_deleted(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Deleting a form from a competition that has none returns APPLICATION_FORM_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_application_form(comp.created.competition_id)

    # Assert
    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_non_owner_organizer_cannot_delete_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.delete_application_form(comp.created.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_delete_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    response = await api_client.delete_application_form(comp.created.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_deleted_form_can_be_replaced_with_new_one(
    gateway: Gateway,
) -> None:
    """After deleting a form, creating a new one for the same competition succeeds."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)
    await gateway.application_form.delete(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    new_form = await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Assert
    assert new_form.application_form_id is not None
