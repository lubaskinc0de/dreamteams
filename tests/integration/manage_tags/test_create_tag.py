import asyncio
from uuid import uuid4

from dreamteams.application.manage_tags import CompetitionTagInput
from dreamteams.entities.competition.tag import CompetitionTag
from tests.integration.api_client import ApiClient, APIResponse
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.race import assert_one_success_one_error

_TAG_CREATION_RACE_ERRORS = frozenset(
    {
        (409, "COMPETITION_TAG_ALREADY_EXISTS"),
        (429, "INTEGRITY_CONFLICT"),
    },
)


async def test_admin_can_create_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can create a competition tag."""
    # Arrange
    admin = await gateway.admin.create()
    tag_input = CompetitionTagInput(value=f"CreateTag-{uuid4()}")

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.create_tag(tag_input.model_dump(mode="json"))).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTag(id=actual.id, value=tag_input.value)


async def test_created_tag_value_is_trimmed(api_client: ApiClient, gateway: Gateway) -> None:
    """Created tag values are normalized by trimming surrounding whitespace."""
    # Arrange
    admin = await gateway.admin.create()
    value = f"TrimmedTag-{uuid4()}"
    tag_input = CompetitionTagInput(value=f"  {value}  ")

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.create_tag(tag_input.model_dump(mode="json"))).assert_status(200).ensure_content()

    # Assert
    assert actual == CompetitionTag(id=actual.id, value=value)


async def test_duplicate_tag_value_is_rejected_case_insensitively(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin cannot create two tags with the same value ignoring case."""
    # Arrange
    admin = await gateway.admin.create()
    value = f"DuplicateTag-{uuid4()}"

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        first = await api_client.create_tag(CompetitionTagInput(value=value).model_dump(mode="json"))
        second = await api_client.create_tag(CompetitionTagInput(value=value.lower()).model_dump(mode="json"))

    # Assert
    first.assert_status(200)
    second.assert_error(409, "COMPETITION_TAG_ALREADY_EXISTS")


async def test_concurrent_duplicate_tag_creation_creates_one_tag(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Concurrent duplicate tag creation creates exactly one tag."""
    # Arrange
    admin = await gateway.admin.create()
    tag_input = CompetitionTagInput(value=f"ConcurrentDuplicateTag-{uuid4()}")
    payload = tag_input.model_dump(mode="json")

    async def create() -> APIResponse[CompetitionTag]:
        with api_client.authenticate(auth_user_id=admin.auth_id):
            return await api_client.create_tag(payload)

    # Act
    responses = await asyncio.gather(create(), create())
    with api_client.authenticate(auth_user_id=admin.auth_id):
        tags = (await api_client.list_admin_tags(search=tag_input.value)).assert_status(200).ensure_content()

    # Assert
    assert_one_success_one_error(responses, _TAG_CREATION_RACE_ERRORS)
    assert tags.total == 1


async def test_non_admin_cannot_create_tag(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot create competition tags."""
    # Arrange
    participant = await gateway.participant.create()
    tag_input = CompetitionTagInput(value=f"NonAdminCreateTag-{uuid4()}")

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.create_tag(tag_input.model_dump(mode="json"))

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_create_tag(api_client: ApiClient) -> None:
    """Unauthenticated requests cannot create competition tags."""
    # Arrange
    tag_input = CompetitionTagInput(value=f"UnauthenticatedCreateTag-{uuid4()}")

    # Act
    response = await api_client.create_tag(tag_input.model_dump(mode="json"))

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_empty_tag_value_is_rejected(api_client: ApiClient, gateway: Gateway) -> None:
    """Empty tag values are rejected by request validation."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.create_tag({"value": ""})

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_too_long_tag_value_is_rejected(api_client: ApiClient, gateway: Gateway) -> None:
    """Tag values longer than 100 characters are rejected by request validation."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.create_tag({"value": "x" * 101})

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_blank_tag_value_is_rejected_after_normalization(api_client: ApiClient, gateway: Gateway) -> None:
    """Whitespace-only tag values are rejected after domain normalization."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.create_tag({"value": "   "})

    # Assert
    response.assert_error(422, "INVALID_COMPETITION_DATA")
