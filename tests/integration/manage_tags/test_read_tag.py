from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_read_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can read a competition tag."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ReadTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.read_tag(tag.id)).assert_status(200).ensure_content()

    # Assert
    assert actual == tag


async def test_non_admin_cannot_read_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot read admin tag details."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["ReadByNonAdminTag"]))[0]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_tag(tag.id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_read_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Unauthenticated requests cannot read admin tag details."""
    # Arrange
    admin = await gateway.admin.create()
    tag = (await gateway.tags.create_many_unique(admin.auth_id, ["UnauthenticatedReadTag"]))[0]

    # Act
    response = await api_client.read_tag(tag.id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_unknown_tag_cannot_be_read(api_client: ApiClient, gateway: Gateway) -> None:
    """Reading an unknown tag returns COMPETITION_TAG_NOT_FOUND."""
    # Arrange
    admin = await gateway.admin.create()
    unknown_tag_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_tag(unknown_tag_id)

    # Assert
    response.assert_error(404, "COMPETITION_TAG_NOT_FOUND")
