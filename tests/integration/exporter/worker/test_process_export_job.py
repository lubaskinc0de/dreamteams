from urllib.parse import quote

import pytest

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.errors.rate_limit import RateLimitExceededError
from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.exporter.facade import ExporterGateway
from tests.integration.exporter.helpers import (
    build_submission_input,
    expected_row,
    export_form,
    prime_rate_limit,
)
from tests.integration.helpers.facade import Gateway


@pytest.mark.parametrize(
    ("count", "accepted_count"),
    [
        (23, 20),
        (43, 40),
    ],
)
async def test_process_job_writes_csv_and_marks_job_successful(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
    count: int,
    accepted_count: int,
) -> None:
    """Process job writes a CSV and marks the export successful."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    await gateway.application_form.create(
        competition.created.competition_id,
        owner.organizer.auth_id,
        export_form(),
    )
    accepted_models = await gateway.application.create_n_accepted_applications(
        n=count,
        accept_count=accepted_count,
        competition=competition,
        submit_application_input=build_submission_input(submit_application_input_factory, competition),
        organizer_auth_id=owner.organizer.auth_id,
    )
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.ACCEPTED,
    )

    # Act
    await exporter_gateway.publish_process(job_id=job.id, auth_user_id=owner.organizer.auth_id)
    model = await exporter_gateway.wait_http_job(
        job_id=job.id,
        auth_user_id=owner.organizer.auth_id,
        status_kind="success",
    )

    # Assert
    assert model == ExportJobModel(
        id=job.id,
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.ACCEPTED,
        status_kind="success",
        status_reason=None,
        file_url=model.file_url,
        created_at=job.created_at,
        finished_at=model.finished_at,
    )
    assert model.file_url is not None
    rows = await exporter_gateway.fetch_csv_rows(model.file_url)
    assert sorted(rows, key=lambda row: row["ID заявки"]) == sorted(
        [expected_row(application) for application in accepted_models],
        key=lambda row: row["ID заявки"],
    )


async def test_process_job_with_no_matching_applications_creates_header_only_csv(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
) -> None:
    """Process job creates a header-only CSV when no applications match."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.REJECTED,
    )

    # Act
    await exporter_gateway.publish_process(job_id=job.id, auth_user_id=owner.organizer.auth_id)
    model = await exporter_gateway.wait_http_job(
        job_id=job.id,
        auth_user_id=owner.organizer.auth_id,
        status_kind="success",
    )

    # Assert
    assert model.file_url is not None
    assert model.finished_at is not None
    assert model == ExportJobModel(
        id=job.id,
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.REJECTED,
        status_kind="success",
        status_reason=None,
        file_url=model.file_url,
        created_at=job.created_at,
        finished_at=model.finished_at,
    )
    rows = await exporter_gateway.fetch_csv_rows(model.file_url)
    text = await exporter_gateway.fetch_csv_text(model.file_url)
    assert rows == []
    assert "ID заявки" in text


async def test_process_job_marks_job_failed_when_rate_limit_is_exceeded(
    exporter_gateway: ExporterGateway,
    exporter_config: ExporterConfig,
    gateway: Gateway,
) -> None:
    """Process job marks the export failed when rate limit is exceeded."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create(owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
    )
    await prime_rate_limit(
        redis_url=exporter_config.cache.url,
        user_id=owner.organizer.created.user_id,
        max_attempts=exporter_config.cache.rate_limit_max,
    )

    # Act
    with pytest.raises(RateLimitExceededError):
        await exporter_gateway.publish_process(job_id=job.id, auth_user_id=owner.organizer.auth_id)
    model = await exporter_gateway.wait_http_job(
        job_id=job.id,
        auth_user_id=owner.organizer.auth_id,
        status_kind="failed",
    )

    # Assert
    assert model.status_reason is not None
    assert "Export rate limit exceeded" in model.status_reason
    assert model == ExportJobModel(
        id=job.id,
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.PENDING,
        status_kind="failed",
        status_reason=model.status_reason,
        file_url=None,
        created_at=job.created_at,
        finished_at=model.finished_at,
    )


async def test_process_job_marks_job_failed_when_main_api_listing_fails(
    exporter_gateway: ExporterGateway,
    exporter_config: ExporterConfig,
    gateway: Gateway,
) -> None:
    """Process job marks the export failed when main API listing fails."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    foreign_owner = await gateway.organizer.create(owner.admin.auth_id)
    competition = await gateway.competition.create_active(foreign_owner.auth_id, auto_accept=False)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
    )

    # Act
    with pytest.raises(ValueError, match="HTTP status assertion failed"):
        await exporter_gateway.publish_process(job_id=job.id, auth_user_id=owner.organizer.auth_id)
    model = await exporter_gateway.wait_http_job(
        job_id=job.id,
        auth_user_id=owner.organizer.auth_id,
        status_kind="failed",
    )

    # Assert
    assert model.status_reason is not None
    assert model.status_reason.startswith("unexpected:")
    assert model == ExportJobModel(
        id=job.id,
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=ApplicationStatus.PENDING,
        status_kind="failed",
        status_reason=model.status_reason,
        file_url=None,
        created_at=job.created_at,
        finished_at=model.finished_at,
    )
    status = await exporter_gateway.fetch_public_file_status(
        f"{exporter_config.s3.public_url}/{quote(f'exports/{job.id}.csv')}",
    )
    assert status == 404
