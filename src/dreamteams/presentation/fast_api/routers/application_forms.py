from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.manage_application_form import (
    ApplicationFormInput,
    ApplicationFormModel,
    CreateApplicationForm,
    CreatedApplicationForm,
    DeleteApplicationForm,
    ReadApplicationForm,
)
from dreamteams.entities.common.identifiers import CompetitionId

router = APIRouter(
    tags=["Application Forms"],
    route_class=DishkaRoute,
    prefix="/competitions",
)


@router.post("/{competition_id}/application-form/")
async def create_application_form(
    interactor: FromDishka[CreateApplicationForm],
    competition_id: CompetitionId,
    data: ApplicationFormInput,
) -> CreatedApplicationForm:
    """HTTP endpoint for creating an application form for a competition."""
    return await interactor.execute(competition_id, data)


@router.get("/{competition_id}/application-form/")
async def read_application_form(
    interactor: FromDishka[ReadApplicationForm],
    competition_id: CompetitionId,
) -> ApplicationFormModel:
    """HTTP endpoint for reading the application form of a competition."""
    return await interactor.execute(competition_id)


@router.delete("/{competition_id}/application-form/")
async def delete_application_form(
    interactor: FromDishka[DeleteApplicationForm],
    competition_id: CompetitionId,
) -> None:
    """HTTP endpoint for deleting the application form of a competition."""
    await interactor.execute(competition_id)
