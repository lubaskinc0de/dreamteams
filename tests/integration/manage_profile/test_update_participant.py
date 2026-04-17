from uuid import uuid4

from faker import Faker

from dreamteams.application.manage_profile import ParticipantModel, ProfileModel
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from tests.common.factory.participant import UpdateParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_participant_profile_is_updated(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that participant profile fields are persisted after update."""
    # Arrange
    participant = await gateway.participant.create()
    update_form = update_participant_form_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        await api_client.update_participant(update_form.model_dump(mode="json"))
        response = await api_client.view_profile()

    # Assert
    profile = response.assert_status(200).ensure_content()
    assert profile.participant is not None

    assert sorted(profile.participant.skills, key=lambda s: s.name) == sorted(
        [ParticipantSkill(name=s.name, level=s.level) for s in update_form.skills],
        key=lambda s: s.name,
    )

    assert profile == ProfileModel(
        user_id=participant.created.user_id,
        organizer=None,
        participant=ParticipantModel(
            id=participant.created.participant_id,
            user_id=participant.created.user_id,
            full_name=update_form.full_name,
            participant_type=update_form.participant_type,
            age=update_form.age,
            bio=update_form.bio,
            skills=profile.participant.skills,
            experience_level=update_form.experience_level,
            preferred_domains=update_form.preferred_domains,
            contacts=[ParticipantContact(title=c.title, url=str(c.url)) for c in update_form.contacts],
        ),
        avatar_url=None,
        is_admin=False,
    )


async def test_update_participant_fails_if_full_name_exceeds_max_length(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test that full_name longer than 70 characters is rejected with 422."""
    data = update_participant_form_factory.build().model_copy(update={"full_name": "a" * 71})

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_full_name_is_empty(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test that empty full_name is rejected with 422."""
    data = update_participant_form_factory.build().model_copy(update={"full_name": ""})

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_bio_exceeds_max_length(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test that bio longer than 500 characters is rejected with 422."""
    data = update_participant_form_factory.build().model_copy(update={"bio": "a" * 501})

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_skill_has_invalid_level(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test that a skill with an invalid level is rejected with 422."""
    data = update_participant_form_factory.build().model_copy(
        update={"skills": [{"name": "Python", "level": ""}]},
    )

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_contact_url_is_malformed(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test that a contact with a malformed URL is rejected with 422."""
    data = update_participant_form_factory.build().model_copy(
        update={"contacts": [{"title": "GitHub", "url": "not-a-url"}]},
    )

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_age_is_negative(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that a negative age is rejected with 400."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build(age=-1)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(400, "INVALID_PARTICIPANT_DATA")


async def test_update_participant_fails_if_age_exceeds_maximum(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that age above 150 is rejected with 400."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build(age=151)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(400, "INVALID_PARTICIPANT_DATA")


async def test_update_participant_fails_if_user_has_no_participant_role(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that updating participant profile returns 404 when user has no participant role."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    update_form = update_participant_form_factory.build()

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.update_participant(update_form.model_dump(mode="json"))

    # Assert
    response.assert_error(404, "PARTICIPANT_NOT_FOUND")


async def test_update_participant_fails_if_unauthorized(
    api_client: ApiClient,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that updating participant profile returns 401 when not authenticated."""
    update_form = update_participant_form_factory.build()

    response = await api_client.update_participant(update_form.model_dump(mode="json"))

    response.assert_error(401, "UNAUTHORIZED")
