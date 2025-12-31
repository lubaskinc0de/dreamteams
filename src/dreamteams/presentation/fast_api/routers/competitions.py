from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.create_competition.interactor import (
    CompetitionForm,
    CreateCompetition,
    CreatedCompetition,
)
from dreamteams.application.delete_competition.interactor import DeleteCompetition
from dreamteams.application.update_competition.interactor import UpdateCompetition, UpdateCompetitionForm
from dreamteams.entities.common.identifiers import CompetitionId

router = APIRouter(
    tags=["Competitions"],
    route_class=DishkaRoute,
    prefix="/competitions",
)


@router.post("/")
async def create_competition(
    interactor: FromDishka[CreateCompetition],
    data: CompetitionForm,
) -> CreatedCompetition:
    """HTTP endpoint for creating a competition."""
    return await interactor.execute(data)


@router.put("/{competition_id}")
async def update_competition(
    interactor: FromDishka[UpdateCompetition],
    competition_id: CompetitionId,
    data: UpdateCompetitionForm,
) -> None:
    """HTTP endpoint for updating a competition."""
    await interactor.execute(competition_id, data)


@router.delete("/{competition_id}")
async def delete_competition(
    interactor: FromDishka[DeleteCompetition],
    competition_id: CompetitionId,
) -> None:
    """HTTP endpoint for deleting a competition."""
    await interactor.execute(competition_id)
