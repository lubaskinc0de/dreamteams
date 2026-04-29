import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams_exporter.entities.errors.job import InvalidJobStatusError
from dreamteams_exporter.entities.export_job.vo.status import JobStatus, JobStatusKind


def test_pending_status_has_no_reason() -> None:
    """Pending status never carries a reason."""
    status = JobStatus.pending()

    assert status == JobStatus(kind=JobStatusKind.PENDING, reason=None)


def test_success_status_has_no_reason() -> None:
    """Success status never carries a reason."""
    status = JobStatus.success()

    assert status == JobStatus(kind=JobStatusKind.SUCCESS, reason=None)


@given(reason=st.text(min_size=1))
def test_failed_status_preserves_its_reason(reason: str) -> None:
    """Failed status round-trips the reason it was constructed with."""
    status = JobStatus.failed(reason)

    assert status == JobStatus(kind=JobStatusKind.FAILED, reason=reason)


def test_failed_status_without_reason_raises() -> None:
    """A failed status must carry a reason — None is rejected."""
    with pytest.raises(InvalidJobStatusError):
        JobStatus(kind=JobStatusKind.FAILED, reason=None)


@given(reason=st.text(min_size=1))
def test_pending_status_with_reason_raises(reason: str) -> None:
    """A reason is only meaningful on the failed kind."""
    with pytest.raises(InvalidJobStatusError):
        JobStatus(kind=JobStatusKind.PENDING, reason=reason)


@given(reason=st.text(min_size=1))
def test_success_status_with_reason_raises(reason: str) -> None:
    """A reason is only meaningful on the failed kind."""
    with pytest.raises(InvalidJobStatusError):
        JobStatus(kind=JobStatusKind.SUCCESS, reason=reason)
