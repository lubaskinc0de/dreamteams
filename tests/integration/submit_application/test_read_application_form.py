from uuid import uuid4

from dreamteams.application.submit_application import ApplicationFormModel
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_participant_can_read_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant receives the full form definition when reading a competition's form."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create(owner.organizer.auth_id)
    created = await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_application_form_for_submission(comp.created.competition_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationFormModel(
        id=created.application_form_id,
        competition_id=comp.created.competition_id,
        created_at=result.created_at,
        fields=result.fields,
    )


async def test_participant_gets_not_found_for_nonexistent_competition(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a form for a non-existent competition is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_application_form_for_submission(uuid4())

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_participant_gets_not_found_when_competition_has_no_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a form for a competition that has none returns APPLICATION_FORM_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_application_form_for_submission(comp.created.competition_id)

    # Assert
    response.assert_error(404, "APPLICATION_FORM_NOT_FOUND")


async def test_non_participant_cannot_read_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer (no participant profile) is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_application_form_for_submission(comp.created.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_read_application_form(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id)

    # Act
    response = await api_client.read_application_form_for_submission(comp.created.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
