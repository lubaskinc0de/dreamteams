from uuid import uuid4

from dreamteams.application.manage_profile import OrganizerModel, ParticipantModel, ProfileModel
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_view_organizer_profile(api_client: ApiClient, gateway: Gateway) -> None:
    """Test viewing organizer profile."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.view_profile()

    # Assert
    profile_model = response.assert_status(200).ensure_content()
    assert profile_model == ProfileModel(
        user_id=organizer.organizer.created.user_id,
        organizer=OrganizerModel(
            id=organizer.organizer.created.organizer_id,
            user_id=organizer.organizer.created.user_id,
            organizer_name=organizer.organizer.form.organizer_name,
            phone_number=organizer.organizer.form.phone_number,
            contact_email=organizer.organizer.email,
        ),
        participant=None,
        avatar_url=None,
        is_admin=False,
    )


async def test_view_organizer_profile_fails_if_user_does_not_exist(
    api_client: ApiClient,
) -> None:
    """Test viewing profile fails if the auth ID is not linked to any user."""
    with api_client.authenticate(auth_user_id=str(uuid4())):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_organizer_profile_fails_if_unauthorized(api_client: ApiClient) -> None:
    """Test viewing organizer profile fails if user is unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_participant_profile(api_client: ApiClient, gateway: Gateway) -> None:
    """Test viewing participant profile."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.view_profile()

    # Assert
    profile_model = response.assert_status(200).ensure_content()
    assert profile_model is not None
    assert profile_model.participant is not None

    # Skills order from DB is not guaranteed; compare sorted
    assert sorted(profile_model.participant.skills, key=lambda s: s.name) == sorted(
        [ParticipantSkill(name=s.name, level=s.level) for s in participant.form.skills],
        key=lambda s: s.name,
    )

    assert profile_model == ProfileModel(
        user_id=participant.created.user_id,
        organizer=None,
        participant=ParticipantModel(
            id=participant.created.participant_id,
            user_id=participant.created.user_id,
            full_name=participant.form.full_name,
            bio=participant.form.bio,
            skills=profile_model.participant.skills,
            experience_level=participant.form.experience_level,
            preferred_domains=participant.form.preferred_domains,
            contacts=[ParticipantContact(title=c.title, url=str(c.url)) for c in participant.form.contacts],
        ),
        avatar_url=None,
        is_admin=False,
    )


async def test_view_participant_profile_fails_if_user_does_not_exist(
    api_client: ApiClient,
) -> None:
    """Test viewing profile fails if the auth ID is not linked to any user."""
    with api_client.authenticate(auth_user_id=str(uuid4())):
        response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_participant_profile_fails_if_unauthorized(api_client: ApiClient) -> None:
    """Test viewing participant profile fails if user is unauthorized."""
    response = await api_client.view_profile()

    response.assert_error(401, "UNAUTHORIZED")
