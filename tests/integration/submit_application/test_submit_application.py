from uuid import uuid4

from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant
from dreamteams.application.submit_application import CreatedApplication, SubmitApplicationInput
from dreamteams.entities.common.vo.domain import Domain
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import PARTICIPANT_USER_ID, USER_ID


async def test_participant_can_submit_application(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
) -> None:
    """Participant receives a valid application_id when submitting to an open competition."""
    # Arrange
    data = submit_application_input.model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(competition.competition_id, data)

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplication(application_id=result.application_id)


async def test_participant_can_submit_application_with_form_data(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Participant may provide form_data matching a competition's ApplicationForm."""
    # Arrange — competition with a single known domain and a required string field in its form
    form = competition_form_factory.build(domains=[Domain.BACKEND])
    with api_client.authenticate(auth_user_id=USER_ID):
        competition_id = (
            (await api_client.create_competition(form.model_dump(mode="json")))
            .assert_status(200)
            .ensure_content()
            .competition_id
        )
        await api_client.create_application_form(
            competition_id,
            {"fields": [{"name": "bio", "label": "Bio", "type": "string", "required": True, "choices": None}]},
        )
    data = submit_application_input_factory.build(
        domains=[Domain.BACKEND],
        form_data={"bio": "My backend experience"},
    )

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(competition_id, data.model_dump(mode="json"))

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result == CreatedApplication(application_id=result.application_id)


async def test_unauthenticated_user_cannot_submit_application(
    api_client: ApiClient,
    competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
) -> None:
    """Unauthenticated requests to submit an application are rejected with UNAUTHORIZED."""
    # Arrange
    data = submit_application_input.model_dump(mode="json")

    # Act
    response = await api_client.submit_application(competition.competition_id, data)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_non_participant_cannot_submit_application(
    api_client: ApiClient,
    competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
) -> None:
    """A user without a participant profile is denied with ACCESS_DENIED."""
    # Arrange
    data = submit_application_input.model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.submit_application(competition.competition_id, data)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_submission_to_nonexistent_competition_fails(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting to a competition that does not exist is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    data = submit_application_input_factory.build(domains=[Domain.BACKEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(uuid4(), data.model_dump(mode="json"))

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_duplicate_submission_is_rejected(
    api_client: ApiClient,
    submitted_application: CreatedApplication,  # noqa: ARG001
    non_autoaccept_competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
) -> None:
    """A participant who already submitted to the same competition is rejected with APPLICATION_ALREADY_EXISTS."""
    # Arrange
    data = submit_application_input.model_dump(mode="json")

    # Act — PARTICIPANT_USER_ID tries to submit again to the same competition
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(non_autoaccept_competition.competition_id, data)

    # Assert
    response.assert_error(409, "APPLICATION_ALREADY_EXISTS")


async def test_domains_outside_competition_are_rejected(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Submitting with domains not offered by the competition is rejected with INVALID_APPLICATION_DATA."""
    # Arrange — competition supports only BACKEND; participant submits FRONTEND
    form = competition_form_factory.build(domains=[Domain.BACKEND])
    with api_client.authenticate(auth_user_id=USER_ID):
        competition_id = (
            (await api_client.create_competition(form.model_dump(mode="json")))
            .assert_status(200)
            .ensure_content()
            .competition_id
        )
    data = submit_application_input_factory.build(domains=[Domain.FRONTEND], form_data=None)

    # Act
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(competition_id, data.model_dump(mode="json"))

    # Assert
    response.assert_error(400, "INVALID_APPLICATION_DATA")
