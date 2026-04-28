from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from tests.common.factory.competition import UpdateCompetitionGeneralInfoFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_general_info_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_general_info_update_as_owner_succeeds(
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
    request_container: AsyncContainer,
) -> None:
    """General information update succeeds for the owning organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    update_form = update_competition_general_info_form_factory.build()

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    current_model = await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id)
    expected_model = competition_general_info_form_to_model(
        competition_id=comp.created.competition_id,
        updated_at=db_competition.updated_at,
        created_at=db_competition.created_at,
        organizer_id=db_competition.organizer_id,
        current=current_model,
        form=update_form,
    )

    # Act
    actual_model = await gateway.competition.update_general_info(
        comp.created.competition_id,
        update_form,
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_general_info_update_persists_tags(
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
    request_container: AsyncContainer,
) -> None:
    """General information update returns attached tag entities on read."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    mobile, backend = await gateway.tags.create_many_unique(
        owner.admin.auth_id,
        ["MobileUpdateTag", "BackendUpdateTag"],
    )

    update_form = update_competition_general_info_form_factory.build(tag_ids=[mobile.id, backend.id])

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    current_model = await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id)
    expected_model = competition_general_info_form_to_model(
        competition_id=comp.created.competition_id,
        updated_at=db_competition.updated_at,
        created_at=db_competition.created_at,
        organizer_id=db_competition.organizer_id,
        current=current_model,
        form=update_form,
        tags=[backend, mobile],
    )

    # Act
    actual_model = await gateway.competition.update_general_info(
        comp.created.competition_id,
        update_form,
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_general_info_update_rejects_more_than_thirty_tag_ids(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update rejects more than 30 tag IDs."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_general_info_form_factory.build().model_dump(mode="json")
    data["tag_ids"] = [str(uuid4()) for _ in range(31)]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition_general_info(comp.created.competition_id, data)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_general_info_update_rejects_empty_description(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update rejects an empty description."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_general_info_form_factory.build().model_copy(update={"description": ""})

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition_general_info(
            comp.created.competition_id,
            data.model_dump(mode="json"),
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_general_info_update_rejects_unknown_tag(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update rejects tag IDs that do not exist."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_general_info_form_factory.build(tag_ids=[uuid4()]).model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition_general_info(comp.created.competition_id, data)

    # Assert
    response.assert_error(404, "COMPETITION_TAG_NOT_FOUND")


async def test_general_info_update_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update fails when user is unauthorized."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_general_info_form_factory.build().model_dump(mode="json")

    # Act
    response = await api_client.update_competition_general_info(comp.created.competition_id, data)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_general_info_update_fails_if_not_owner(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update fails when user is not the owner."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = update_competition_general_info_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.update_competition_general_info(comp.created.competition_id, data)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_general_info_update_fails_if_not_found(
    api_client: ApiClient,
    gateway: Gateway,
    update_competition_general_info_form_factory: UpdateCompetitionGeneralInfoFormFactory,
) -> None:
    """General information update fails when competition does not exist."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = update_competition_general_info_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.update_competition_general_info(uuid4(), data)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")
