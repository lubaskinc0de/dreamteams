from uuid import uuid4

from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from tests.integration.api_client import ApiClient
from tests.integration.exporter.facade import ExporterGateway
from tests.integration.helpers.facade import Gateway


async def test_owner_reads_seeded_pending_export_job(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
) -> None:
    """Owner reads a pending export job."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create(owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.PENDING,
    )

    # Act
    response = await exporter_gateway.read(auth_user_id=owner.organizer.auth_id, job_id=job.id)

    # Assert
    model = response.assert_status(200).ensure_content()
    assert model == job


async def test_owner_reads_seeded_successful_export_job(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
) -> None:
    """Owner reads a successful export job."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create(owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.ACCEPTED,
        finished_status="success",
    )

    # Act
    response = await exporter_gateway.read(auth_user_id=owner.organizer.auth_id, job_id=job.id)

    # Assert
    model = response.assert_status(200).ensure_content()
    assert model == job


async def test_owner_reads_seeded_failed_export_job(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
) -> None:
    """Owner reads a failed export job."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create(owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.REJECTED,
        finished_status="failed",
        failed_reason="seeded failure",
    )

    # Act
    response = await exporter_gateway.read(auth_user_id=owner.organizer.auth_id, job_id=job.id)

    # Assert
    model = response.assert_status(200).ensure_content()
    assert model == job


async def test_other_organizer_cannot_read_export_job(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
) -> None:
    """Other organizer cannot read another organizer's export job."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    intruder = await gateway.organizer.create(owner.admin.auth_id)
    competition = await gateway.competition.create(owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
    )

    # Act
    response = await exporter_gateway.read(auth_user_id=intruder.auth_id, job_id=job.id)

    # Assert
    response.assert_error(404, "EXPORT_JOB_NOT_FOUND")


async def test_unknown_export_job_is_not_found(
    exporter_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unknown export job is not found."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with exporter_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await exporter_client.read_export(uuid4())

    # Assert
    response.assert_error(404, "EXPORT_JOB_NOT_FOUND")


async def test_missing_auth_cannot_read_export_job(
    exporter_client: ApiClient,
) -> None:
    """Missing auth is rejected when reading an export job."""
    # Arrange
    job_id = uuid4()

    # Act
    response = await exporter_client.read_export(job_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
