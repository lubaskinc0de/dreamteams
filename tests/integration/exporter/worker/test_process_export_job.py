import csv
import io
from urllib.parse import quote

import pytest

from dreamteams.application.common.dto.application import ApplicationModel
from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.errors.rate_limit import RateLimitExceededError
from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.exporter.facade import ExporterGateway
from tests.integration.exporter.helpers import (
    build_submission_input,
    export_form,
    prime_rate_limit,
)
from tests.integration.helpers.facade import Gateway

EXPECTED_BASE_HEADERS = [
    "ФИО",
    "Соревнование",
    "Статус",
    "Направления",
    "Возраст",
    "Тип участника",
    "Контакты",
    "Дата",
]
EXPECTED_FORM_HEADERS = [
    *EXPECTED_BASE_HEADERS[:7],
    "motivation",
    "roles",
    *EXPECTED_BASE_HEADERS[7:],
]


def _sort_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: tuple(row.items()))


def _read_headers(text: str) -> list[str]:
    return next(csv.reader(io.StringIO(text)))


def _unsigned_object_url(exporter_config: ExporterConfig, key: str) -> str:
    base = exporter_config.s3.download_endpoint_url.rstrip("/")
    return f"{base}/{exporter_config.s3.bucket_name}/{quote(key)}"


def expected_row(application: ApplicationModel) -> dict[str, str]:
    """Project an application into the expected process-job CSV row."""
    form_data = application.form_data or {}
    return {
        "ФИО": application.participant.full_name,
        "Соревнование": application.competition_name,
        "Статус": application.status.value,
        "Направления": application.track.name,
        "Возраст": str(application.participant.age),
        "Тип участника": application.participant.participant_type.value,
        "Контакты": ", ".join(f"{c.title}: {c.value}" for c in application.participant.contacts),
        "motivation": str(form_data.get("motivation", "")),
        "roles": ", ".join(str(item) for item in form_data.get("roles", [])),
        "Дата": application.created_at.strftime("%d.%m.%Y %H:%M"),
    }


@pytest.mark.parametrize(
    ("count", "accepted_count"),
    [
        (23, 20),
        (43, 40),
    ],
)
async def test_process_job_writes_csv_and_marks_job_successful(
    exporter_gateway: ExporterGateway,
    exporter_config: ExporterConfig,
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
    assert "X-Amz-Expires=900" in model.file_url
    assert "X-Amz-Signature=" in model.file_url
    rows = await exporter_gateway.fetch_csv_rows(model.file_url)
    text = await exporter_gateway.fetch_csv_text(model.file_url)
    raw_status = await exporter_gateway.fetch_public_file_status(
        _unsigned_object_url(exporter_config, f"exports/{job.id}.csv"),
    )
    assert _read_headers(text) == EXPECTED_FORM_HEADERS
    assert _sort_rows(rows) == _sort_rows([expected_row(application) for application in accepted_models])
    assert raw_status != 200


async def test_process_unfiltered_job_writes_applications_with_all_statuses(
    exporter_gateway: ExporterGateway,
    gateway: Gateway,
    submit_application_input_factory: SubmitApplicationInputFactory,
) -> None:
    """Unfiltered process job exports applications regardless of status."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    competition = await gateway.competition.create_active(owner.organizer.auth_id, auto_accept=False)
    await gateway.application_form.create(
        competition.created.competition_id,
        owner.organizer.auth_id,
        export_form(),
    )
    submitted_ids = await gateway.application.create_for_competition(
        6,
        competition.created.competition_id,
        build_submission_input(submit_application_input_factory, competition),
    )
    all_models = await gateway.application.create_mixed(submitted_ids, owner.organizer.auth_id)
    job = await exporter_gateway.seed(
        user_id=owner.organizer.created.user_id,
        competition_id=competition.created.competition_id,
        application_status=None,
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
        application_status=None,
        status_kind="success",
        status_reason=None,
        file_url=model.file_url,
        created_at=job.created_at,
        finished_at=model.finished_at,
    )
    assert model.file_url is not None
    rows = await exporter_gateway.fetch_csv_rows(model.file_url)
    assert _sort_rows(rows) == _sort_rows([expected_row(application) for application in all_models])


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
    assert _read_headers(text) == EXPECTED_BASE_HEADERS


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
        _unsigned_object_url(exporter_config, f"exports/{job.id}.csv"),
    )
    assert status != 200
