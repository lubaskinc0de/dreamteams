from uuid import uuid4

from faker import Faker

from dreamteams.application.common.dto.participant_contact import MAX_CONTACT_VALUE_LENGTH, ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import MAX_PARTICIPANT_SKILLS, ParticipantSkillForm
from dreamteams.application.manage_profile import ParticipantModel, ProfileModel
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_skill import ParticipantSkill, SkillLevel
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

    expected_contacts = sorted(
        [ParticipantContact(title=c.title, value=c.value) for c in update_form.contacts],
        key=lambda c: c.title,
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
            contacts=expected_contacts,
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
    data = update_participant_form_factory.build().model_dump(mode="json")
    data["skills"] = [{"name": "Python", "level": ""}]

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.update_participant(data)

    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_accepts_non_url_contact_value(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that a contact value does not need URL syntax."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_copy(
        update={"contacts": [ParticipantContactForm(title="Telegram", value="@telegram")]},
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_status(200)


async def test_update_participant_rejects_more_than_fifteen_contacts(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Updating a participant with more than 15 contacts is rejected by request validation."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_dump(mode="json")
    data["contacts"] = [{"title": f"contact-{i}", "value": f"https://example.com/{i}"} for i in range(16)]

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_rejects_too_many_skills(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Updating a participant with too many skills is rejected by request validation."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_copy(
        update={
            "skills": [
                ParticipantSkillForm(name=f"skill-{i}", level=SkillLevel.BEGINNER)
                for i in range(MAX_PARTICIPANT_SKILLS + 1)
            ],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_rejects_too_long_contact_value(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Updating a participant with an oversized contact value is rejected by request validation."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_copy(
        update={
            "contacts": [
                ParticipantContactForm.model_construct(
                    title="Telegram",
                    value="a" * (MAX_CONTACT_VALUE_LENGTH + 1),
                ),
            ],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_age_is_negative(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that a negative age is rejected by request validation."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_copy(update={"age": -1})

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_update_participant_fails_if_age_exceeds_maximum(
    api_client: ApiClient,
    gateway: Gateway,
    update_participant_form_factory: UpdateParticipantFormFactory,
) -> None:
    """Test that age above 150 is rejected by request validation."""
    # Arrange
    participant = await gateway.participant.create()
    data = update_participant_form_factory.build().model_copy(update={"age": 151})

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.update_participant(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


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
