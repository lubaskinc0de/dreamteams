from uuid import uuid4

from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_delete_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can delete a competition tag."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["DeleteTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        delete_response = await api_client.delete_tag(tag.id)
        read_after_delete = await api_client.read_tag(tag.id)

    # Assert
    delete_response.assert_status(200)
    read_after_delete.assert_error(404, "COMPETITION_TAG_NOT_FOUND")


async def test_admin_can_delete_tag_attached_to_competition(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Deleting a tag also removes it from competitions that referenced it."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    tag = (await gateway.tags.create_many_unique(owner.admin.auth_id, ["AttachedDeleteTag"]))[0]
    form = competition_form_factory.build(tag_ids=[tag.id])
    competition = await gateway.competition.create_from_form(owner.organizer.auth_id, form)

    # Act
    with api_client.authenticate(auth_user_id=owner.admin.auth_id):
        response = await api_client.delete_tag(tag.id)
    actual = await gateway.competition.read(competition.id, owner.organizer.auth_id)

    # Assert
    response.assert_status(200)
    assert actual == competition.model_copy(update={"tags": []})


async def test_non_admin_cannot_delete_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot delete competition tags."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["NonAdminDeleteTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.delete_tag(tag.id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_delete_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Unauthenticated requests cannot delete competition tags."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["UnauthenticatedDeleteTag"]))[0]

    # Act
    response = await api_client.delete_tag(tag.id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_unknown_tag_cannot_be_deleted(api_client: ApiClient, gateway: Gateway) -> None:
    """Deleting an unknown tag returns COMPETITION_TAG_NOT_FOUND."""
    # Arrange
    admin = await gateway.admin.create()
    unknown_tag_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.delete_tag(unknown_tag_id)

    # Assert
    response.assert_error(404, "COMPETITION_TAG_NOT_FOUND")
