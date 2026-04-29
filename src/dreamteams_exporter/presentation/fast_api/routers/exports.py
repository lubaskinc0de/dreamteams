from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.export_applications_sheets.create_job import (
    CreatedExportJob,
    CreateExportApplicationsJob,
    CreateExportJobInput,
)
from dreamteams_exporter.application.export_applications_sheets.read_job import (
    ReadExportApplicationsJob,
    ReadExportJobInput,
)
from dreamteams_exporter.entities.common.identifiers import ExportJobId

router = APIRouter(
    tags=["Exports"],
    route_class=DishkaRoute,
    prefix="/exports",
)


@router.post("/")
async def create_export(
    interactor: FromDishka[CreateExportApplicationsJob],
    data: CreateExportJobInput,
) -> CreatedExportJob:
    """Creates a pending export job and schedules the worker to process it."""
    return await interactor.execute(data)


@router.get("/{job_id}")
async def read_export(
    interactor: FromDishka[ReadExportApplicationsJob],
    job_id: ExportJobId,
) -> ExportJobModel:
    """Returns the state of an export job owned by the caller."""
    return await interactor.execute(ReadExportJobInput(job_id=job_id))
