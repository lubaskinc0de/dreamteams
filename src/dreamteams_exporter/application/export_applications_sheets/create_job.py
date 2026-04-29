from dataclasses import dataclass

import structlog

from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_exporter.application.common.event_bus import EventBus, JobEventBus
from dreamteams_exporter.application.common.events import ExportJobCreated, ExportJobEnqueued
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.entities.common.identifiers import CompetitionId, ExportJobId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.errors.user import InvalidRoleError
from dreamteams_exporter.entities.export_job.factory import export_job_factory


@dataclass(slots=True, kw_only=True, frozen=True)
class CreateExportJobInput:
    """Payload accepted by the create-job interactor."""

    competition_id: CompetitionId
    application_status: ApplicationStatus | None = None


@dataclass(slots=True, kw_only=True, frozen=True)
class CreatedExportJob:
    """Result returned by the create-job interactor."""

    job_id: ExportJobId


logger: Logger = structlog.get_logger(__name__)


@interactor
class CreateExportApplicationsJob:
    """Interactor that persists a new export job and publishes it for processing."""

    gateway: ExportJobGateway
    idp: IdProvider
    job_event_bus: JobEventBus
    event_bus: EventBus
    clock: Clock

    async def execute(self, data: CreateExportJobInput) -> CreatedExportJob:
        """Persist a pending job for the authenticated user and publish it for processing."""
        user = await self.idp.get_user()
        if user.organizer_id is None:
            raise InvalidRoleError(message="Only organizers may export applications")
        logger.info(
            "Creating export job",
            user_id=user.user_id,
            competition_id=data.competition_id,
            application_status=data.application_status,
        )
        job = export_job_factory(
            user_id=user.user_id,
            competition_id=data.competition_id,
            application_status=data.application_status,
            clock=self.clock,
        )
        await self.gateway.create(job)
        await self.event_bus.publish(ExportJobCreated(application_status=job.application_status))

        await self.job_event_bus.publish_process(job.id)
        await self.event_bus.publish(ExportJobEnqueued(application_status=job.application_status))
        return CreatedExportJob(job_id=job.id)
