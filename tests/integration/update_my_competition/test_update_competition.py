from typing import Any
from uuid import uuid4

import pytest
from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.clock import Clock
from tests.common.factory.competition import UpdateCompetitionFormFactory
from tests.common.helpers.competition import (
    INVALID_COMPETITION_DATA_CASES,
    milestones_from_deltas,
    schedule_from_deltas,
)
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_update_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_update_competition_as_owner_succeeds(
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Test updating competition as owner."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    update_form = update_competition_form_factory.build()

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    expected_model = competition_update_form_to_model(
        competition_id=comp.created.competition_id,
        updated_at=db_competition.updated_at,
        created_at=db_competition.created_at,
        organizer_id=db_competition.organizer_id,
        form=update_form,
        clock=clock,
    )

    # Act
    actual_model = await gateway.competition.update(
        comp.created.competition_id,
        update_form,
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_update_competition_persists_tags(
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Updating a competition with tag_ids returns the attached tag entities on read."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    mobile, backend = await gateway.tags.create_many_unique(
        owner.admin.auth_id,
        ["MobileUpdateTag", "BackendUpdateTag"],
    )

    update_form = update_competition_form_factory.build(tag_ids=[mobile.id, backend.id])

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    expected_model = competition_update_form_to_model(
        competition_id=comp.created.competition_id,
        updated_at=db_competition.updated_at,
        created_at=db_competition.created_at,
        organizer_id=db_competition.organizer_id,
        form=update_form,
        clock=clock,
        tags=[backend, mobile],
    )

    # Act
    actual_model = await gateway.competition.update(
        comp.created.competition_id,
        update_form,
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_update_competition_rejects_more_than_thirty_tag_ids(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Updating a competition with more than 30 tag_ids is rejected by request validation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_form_factory.build().model_dump(mode="json")
    data["tag_ids"] = [str(uuid4()) for _ in range(31)]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_competition_fails_if_description_is_empty(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test updating competition with empty description is rejected with 422."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_form_factory.build().model_copy(update={"description": ""})

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_update_competition_with_invalid_data(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test updating competition with invalid data."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    base_data = update_competition_form_factory.build().model_dump(mode="json")
    update_data = update_data.copy()

    if "schedule" in update_data:
        update_data["schedule"] = schedule_from_deltas(**update_data["schedule"])
    if "milestones" in update_data:
        update_data["milestones"] = milestones_from_deltas(update_data["milestones"])
    base_data.update(update_data)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition(comp.created.competition_id, base_data)

    # Assert
    response.assert_error(422, expected_error)


async def test_update_competition_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test updating competition fails when user is unauthorized."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_form_factory.build().model_dump(mode="json")

    # Act
    response = await api_client.update_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_update_competition_fails_if_not_owner(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test updating competition fails when user is not the owner."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.update_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_update_competition_fails_if_not_found(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test updating competition fails when competition does not exist."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    non_existent_id = uuid4()
    data = update_competition_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition(non_existent_id, data)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")
