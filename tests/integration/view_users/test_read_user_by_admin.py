from uuid import uuid4

from dreamteams.application.block_user import (
    AdminOrganizerModel,
    AdminParticipantModel,
    AdminUserDetails,
    AdminUserModel,
)
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_skill import ParticipantSkill
from dreamteams.entities.user import BanStatus
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_read_blocked_participant_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can read full participant details for a blocked user."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    reason = "policy"
    await gateway.admin.block_user(admin.auth_id, participant.created.user_id, reason=reason)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_admin_user(participant.created.user_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result.participant is not None
    expected_skills = sorted(
        [ParticipantSkill(name=s.name, level=s.level) for s in participant.form.skills],
        key=lambda skill: skill.name,
    )
    expected_contacts = sorted(
        [ParticipantContact(title=c.title, value=c.value) for c in participant.form.contacts],
        key=lambda contact: contact.title,
    )
    assert result == AdminUserDetails(
        user=AdminUserModel(
            id=participant.created.user_id,
            avatar_url=None,
            is_admin=False,
            ban_status=BanStatus(
                is_blocked=True,
                reason=reason,
                blocked_at=result.user.ban_status.blocked_at,
            ),
        ),
        organizer=None,
        participant=AdminParticipantModel(
            id=participant.created.participant_id,
            user_id=participant.created.user_id,
            full_name=participant.form.full_name,
            participant_type=participant.form.participant_type,
            age=participant.form.age,
            bio=participant.form.bio,
            skills=expected_skills,
            experience_level=participant.form.experience_level,
            contacts=expected_contacts,
            created_at=result.participant.created_at,
            updated_at=result.participant.updated_at,
        ),
    )


async def test_admin_can_read_organizer_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can read organizer profile details for a user."""
    # Arrange
    admin = await gateway.admin.create()
    organizer = await gateway.organizer.create(admin.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_admin_user(organizer.created.user_id)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == AdminUserDetails(
        user=AdminUserModel(
            id=organizer.created.user_id,
            avatar_url=None,
            is_admin=False,
            ban_status=BanStatus(is_blocked=False, reason=None, blocked_at=None),
        ),
        organizer=AdminOrganizerModel(
            id=organizer.created.organizer_id,
            user_id=organizer.created.user_id,
            organizer_name=organizer.form.organizer_name,
            phone_number=organizer.form.phone_number,
            contact_email=organizer.email,
        ),
        participant=None,
    )


async def test_non_admin_cannot_read_user_by_admin(api_client: ApiClient, gateway: Gateway) -> None:
    """Non-admin users cannot read admin user details."""
    # Arrange
    participant = await gateway.participant.create()
    target = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_admin_user(target.user_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_read_user_by_admin(api_client: ApiClient, gateway: Gateway) -> None:
    """Unauthenticated requests cannot read admin user details."""
    # Arrange
    target = await gateway.admin.create()

    # Act
    response = await api_client.read_admin_user(target.user_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_read_user_by_admin_returns_not_found_for_unknown_user(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading an unknown target user returns USER_NOT_FOUND."""
    # Arrange
    admin = await gateway.admin.create()
    unknown_user_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_admin_user(unknown_user_id)

    # Assert
    response.assert_error(404, "USER_NOT_FOUND")
