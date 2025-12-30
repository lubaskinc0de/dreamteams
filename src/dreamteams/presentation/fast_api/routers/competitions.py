from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.create_competition.interactor import (
    CompetitionForm,
    CreateCompetition,
    CreatedCompetition,
)

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
