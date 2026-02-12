from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from dreamteams.application.manage_competitions import (
    CompetitionModel,
    CompetitionsList,
    DeleteCompetition,
    ListCompetitions,
    ListCompetitionsInput,
    ReadCompetition,
    UpdateCompetition,
    UpdateCompetitionForm,
)
from dreamteams.application.preview_competition.list import (
    PreviewCompetitions,
    PreviewCompetitionsInput,
    PreviewCompetitionsList,
)
from dreamteams.application.publish_competition import CompetitionForm, CreateCompetition, CreatedCompetition
from dreamteams.entities.common.identifiers import CompetitionId

router = APIRouter(
    tags=["Competitions"],
    route_class=DishkaRoute,
    prefix="/competitions",
)


@router.get("/preview")
async def preview_competitions(
    interactor: FromDishka[PreviewCompetitions],
    input_data: Annotated[PreviewCompetitionsInput, Query()],
) -> PreviewCompetitionsList:
    """HTTP endpoint for preview listing competitions."""
    return await interactor.execute(input_data)


@router.get("/")
async def list_competitions(
    interactor: FromDishka[ListCompetitions],
    input_data: Annotated[ListCompetitionsInput, Query()],
) -> CompetitionsList:
    """HTTP endpoint for listing competitions."""
    return await interactor.execute(input_data)


@router.post("/")
async def create_competition(
    interactor: FromDishka[CreateCompetition],
    data: CompetitionForm,
) -> CreatedCompetition:
    """HTTP endpoint for creating a competition."""
    return await interactor.execute(data)


@router.get("/{competition_id}")
async def read_competition(
    interactor: FromDishka[ReadCompetition],
    competition_id: CompetitionId,
) -> CompetitionModel:
    """HTTP endpoint for reading a competition by ID."""
    return await interactor.execute(competition_id)


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
