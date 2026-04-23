from datetime import datetime
from uuid import uuid4

import pytest

from dreamteams_common.clock import Clock
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.errors.job import InvalidJobStatusTransitionError
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob
from dreamteams_exporter.entities.export_job.vo.status import JobStatus
from tests.unit.conftest import NOW


def make_pending_job(
    *,
    application_status: ApplicationStatus = ApplicationStatus.PENDING,
    created_at: datetime = NOW,
) -> ExportApplicationsJob:
    """Build a fresh pending job with deterministic defaults."""
    return ExportApplicationsJob(
        id=uuid4(),
        user_id=uuid4(),
        competition_id=uuid4(),
        application_status=application_status,
        status=JobStatus.pending(),
        file_url=None,
        created_at=created_at,
        finished_at=None,
    )


def test_mark_success_transitions_pending_to_success(clock: Clock) -> None:
    """mark_success flips the status to success with the given file_url and finished_at."""
    job = make_pending_job()

    job.mark_success("https://example.com/file.xlsx", clock)

    assert job.status == JobStatus.success()
    assert job.file_url == "https://example.com/file.xlsx"
    assert job.finished_at == NOW


def test_mark_failed_transitions_pending_to_failed_with_reason(clock: Clock) -> None:
    """mark_failed flips the status to failed with the given reason and finished_at."""
    job = make_pending_job()

    job.mark_failed("upload aborted", clock)

    assert job.status == JobStatus.failed("upload aborted")
    assert job.file_url is None
    assert job.finished_at == NOW


def test_cannot_mark_success_from_success_state(clock: Clock) -> None:
    """A successful job cannot be marked success again."""
    job = make_pending_job()
    job.mark_success("https://example.com/file.xlsx", clock)

    with pytest.raises(InvalidJobStatusTransitionError):
        job.mark_success("https://example.com/other.xlsx", clock)


def test_cannot_mark_failed_from_success_state(clock: Clock) -> None:
    """A successful job cannot be flipped to failed."""
    job = make_pending_job()
    job.mark_success("https://example.com/file.xlsx", clock)

    with pytest.raises(InvalidJobStatusTransitionError):
        job.mark_failed("late error", clock)


def test_cannot_mark_success_from_failed_state(clock: Clock) -> None:
    """A failed job cannot be flipped to success."""
    job = make_pending_job()
    job.mark_failed("some reason", clock)

    with pytest.raises(InvalidJobStatusTransitionError):
        job.mark_success("https://example.com/file.xlsx", clock)


def test_cannot_mark_failed_from_failed_state(clock: Clock) -> None:
    """A failed job cannot be marked failed again."""
    job = make_pending_job()
    job.mark_failed("first reason", clock)

    with pytest.raises(InvalidJobStatusTransitionError):
        job.mark_failed("second reason", clock)
