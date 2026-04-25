from uuid import uuid4

from adaptix import Retort
from faststream.nats.publisher.usecase import LogicPublisher

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.export_applications_sheets.create import CreateExportJobInput
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.exporter.facade import ExporterGateway
from tests.integration.helpers.facade import Gateway

_retort = Retort()


async def test_organizer_creates_pending_export_job_and_publishes_message(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
    process_job_publisher: LogicPublisher,
) -> None:
    """Organizer creates a pending export job and publishes its process message."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)

    # Act
    model = await exporter_gateway.create(
        auth_user_id=owner.organizer.auth_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.PENDING,
    )

    # Assert
    assert model == ExportJobModel(
        id=model.id,
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.PENDING,
        status_kind="pending",
        status_reason=None,
        file_url=None,
        created_at=model.created_at,
        finished_at=None,
    )
    process_job_publisher.mock.assert_called_once_with({"job_id": str(model.id)})


async def test_participant_cannot_create_export_job(
    exporter_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Participant cannot create an export job."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with exporter_client.authenticate(auth_user_id=participant.auth_id):
        response = await exporter_client.create_export(
            _retort.dump(
                CreateExportJobInput(competition_id=uuid4(), application_status=ApplicationStatus.PENDING),
            ),
        )

    # Assert
    response.assert_error(403, "INVALID_ROLE")


async def test_missing_auth_cannot_create_export_job(
    exporter_client: ApiClient,
) -> None:
    """Missing auth is rejected when creating an export job."""
    # Act
    response = await exporter_client.create_export(
        _retort.dump(
            CreateExportJobInput(competition_id=uuid4(), application_status=ApplicationStatus.PENDING),
            CreateExportJobInput,
        ),
    )

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_invalid_payload_is_rejected_when_creating_export_job(
    exporter_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Invalid create-export payload is rejected."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with exporter_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await exporter_client.create_export({"application_status": "not-a-status"})

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")
