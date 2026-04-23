from uuid import uuid4

from hypothesis import given
from hypothesis import strategies as st

from dreamteams_common.clock import Clock
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob
from dreamteams_exporter.entities.export_job.factory import export_job_factory
from dreamteams_exporter.entities.export_job.vo.status import JobStatus
from tests.unit.conftest import NOW


@given(status=st.sampled_from(ApplicationStatus))
def test_factory_creates_pending_job_with_requested_fields(clock: Clock, status: ApplicationStatus) -> None:
    """Factory returns a pending job echoing the caller's inputs and the clock's moment."""
    user_id = uuid4()
    competition_id = uuid4()

    job = export_job_factory(
        user_id=user_id,
        competition_id=competition_id,
        application_status=status,
        clock=clock,
    )

    assert job == ExportApplicationsJob(
        id=job.id,
        user_id=user_id,
        competition_id=competition_id,
        application_status=status,
        status=JobStatus.pending(),
        file_url=None,
        created_at=NOW,
        finished_at=None,
    )


def test_factory_generates_unique_ids(clock: Clock) -> None:
    """Two successive factory calls produce distinct job ids."""
    user_id = uuid4()
    competition_id = uuid4()

    job_a = export_job_factory(
        user_id=user_id,
        competition_id=competition_id,
        application_status=ApplicationStatus.PENDING,
        clock=clock,
    )
    job_b = export_job_factory(
        user_id=user_id,
        competition_id=competition_id,
        application_status=ApplicationStatus.PENDING,
        clock=clock,
    )

    assert job_a.id != job_b.id
