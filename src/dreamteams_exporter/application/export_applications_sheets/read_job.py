from dataclasses import dataclass

import structlog

from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.entities.common.identifiers import ExportJobId


@dataclass(slots=True, kw_only=True, frozen=True)
class ReadExportJobInput:
    """Payload accepted by the read-job interactor."""

    job_id: ExportJobId


logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadExportApplicationsJob:
    """Interactor that returns the state of a previously-created export job to its owner."""

    idp: IdProvider
    gateway: ExportJobGateway

    async def execute(self, data: ReadExportJobInput) -> ExportJobModel:
        """Return the job's read model when the caller owns it, otherwise raise JobNotFoundError."""
        user = await self.idp.get_user()
        model = await self.gateway.read(data.job_id)
        if model is None or model.user_id != user.user_id:
            raise JobNotFoundError
        return model
