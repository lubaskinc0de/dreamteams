from uuid import uuid4

from dreamteams.application.common.dto.application import ParticipantInfo
from dreamteams.application.manage_applications import ApplicationModel
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_organizer_can_read_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Competition organizer can read an application submitted to their competition."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_application(application_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == ApplicationModel(
        id=application_id,
        competition_id=comp.created.competition_id,
        competition_name=comp.form.title,
        track=result.track,
        status=ApplicationStatus.PENDING,
        created_at=result.created_at,
        form_data=None,
        participant=ParticipantInfo(
            id=result.participant.id,
            full_name=participant.form.full_name,
            bio=participant.form.bio,
            participant_type=participant.form.participant_type,
            age=participant.form.age,
            skills=sorted(
                [ParticipantSkill(name=s.name, level=s.level) for s in participant.form.skills],
                key=lambda s: s.name,
            ),
            experience_level=participant.form.experience_level,
            contacts=sorted(
                [ParticipantContact(title=c.title, value=c.value) for c in participant.form.contacts],
                key=lambda c: c.title,
            ),
        ),
    )


async def test_unauthenticated_cannot_read_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests to read an application are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_owner_organizer_cannot_read_application(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer who does not own the competition is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_withdrawn_application_cannot_be_read_by_organizer(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a withdrawn application returns APPLICATION_NOT_FOUND for the organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    application_id = await gateway.application.submit(participant.auth_id, comp)
    await gateway.application.withdraw(application_id, participant.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_application(application_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")


async def test_reading_nonexistent_application_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading an application that does not exist is rejected with APPLICATION_NOT_FOUND."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    nonexistent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_application(nonexistent_id)

    # Assert
    response.assert_error(404, "APPLICATION_NOT_FOUND")
