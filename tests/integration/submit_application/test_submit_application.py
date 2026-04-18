from uuid import uuid4

from dreamteams.application.explore_competitions import CreatedApplication
from dreamteams.application.manage_application_form import ApplicationFormInput
from dreamteams.application.manage_application_form.create import FieldForm
from dreamteams.entities.application_form.vo.field import FieldType
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_participant_can_submit_application(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Participant receives a valid application_id when submitting to an open competition."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id)
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplication(application_id=result.application_id)


async def test_participant_can_submit_application_with_form_data(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Participant may provide form_data matching a competition's ApplicationForm."""
    # Arrange — competition with BACKEND domain and a required string field in its form
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()

    comp = await gateway.competition.create_active(owner.organizer.auth_id, domains=[Domain.BACKEND])
    bio_form = ApplicationFormInput(
        fields=[FieldForm(name="bio", label="Bio", type=FieldType.STRING, required=True, choices=None)],
    )
    await gateway.application_form.create(comp.created.competition_id, owner.organizer.auth_id, bio_form)

    data = submit_application_input_factory.build(domains=[Domain.BACKEND], form_data={"bio": "My backend experience"})

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplication(application_id=result.application_id)


async def test_unauthenticated_user_cannot_submit_application(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Unauthenticated requests to submit an application are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    # Act
    response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_participant_cannot_submit_application(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """A user without a participant profile is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id)
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    # Act — owner is an organizer, not a participant
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_submission_to_nonexistent_competition_fails(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting to a competition that does not exist is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    participant = await gateway.participant.create()
    data = submit_application_input_factory.build(domains=[Domain.BACKEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(uuid4(), data.model_dump(mode="json"))

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_duplicate_submission_is_rejected(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """A participant who already submitted to the same competition is rejected with APPLICATION_ALREADY_EXISTS."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    await gateway.application.submit(participant.auth_id, comp)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_EXISTS")


async def test_domains_outside_competition_are_rejected(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting with domains not offered by the competition is rejected with INVALID_APPLICATION_DATA."""
    # Arrange — competition supports only BACKEND; participant submits FRONTEND
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_active(owner.organizer.auth_id, domains=[Domain.BACKEND])
    data = submit_application_input_factory.build(domains=[Domain.FRONTEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_DATA")


async def test_archived_competition_rejects_submission(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting to an archived competition (default state after creation) is rejected with COMPETITION_NOT_ACTIVE."""
    # Arrange — competition is archived by default
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(409, "COMPETITION_NOT_ACTIVE")


async def test_registration_not_open_rejects_submission(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting to an unarchived competition whose registration hasn't started yet is rejected."""
    # Arrange — unarchive without opening registration (schedule stays in the future)
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create_unarchived(owner.organizer.auth_id, domains=[Domain.BACKEND])
    data = submit_application_input_factory.build(domains=[Domain.BACKEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(409, "COMPETITION_NOT_ACTIVE")


async def test_participant_type_mismatch_rejects_submission(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """A STUDENT participant is rejected from a SCHOOLCHILD-only competition."""
    # Arrange — create and open a SCHOOLCHILD-only competition
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    student = await gateway.participant.create(participant_type=ParticipantType.STUDENT)
    comp = await gateway.competition.create_active(
        owner.organizer.auth_id,
        domains=[Domain.BACKEND],
        participant_type=ParticipantType.SCHOOLCHILD,
    )
    data = submit_application_input_factory.build(domains=[Domain.BACKEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=student.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "PARTICIPANT_TYPE_MISMATCH")


async def test_full_competition_rejects_submission(
    api_client: ApiClient,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """A competition at its participant limit rejects further submissions with PARTICIPANT_LIMITS_EXCEEDED."""
    # Arrange — competition with max_participants=1 and auto_accept=True
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=True, max_participants=1)

    # First participant fills the only slot
    first_participant = await gateway.participant.create()
    await gateway.application.submit(first_participant.auth_id, comp)

    second_participant = await gateway.participant.create()
    data = submit_application_input_factory.build(domains=[comp.form.domains[0]], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=second_participant.auth_id):
        response = await api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(409, "PARTICIPANT_LIMITS_EXCEEDED")
