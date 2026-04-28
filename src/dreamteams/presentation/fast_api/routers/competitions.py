from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from dreamteams.application.delete_my_competition import (
    CompetitionModel,
    CompetitionsList,
    DeleteCompetition,
    ListCompetitions,
    ListCompetitionsInput,
)
from dreamteams.application.delete_my_competition import ReadCompetition as ReadCompetitionAsOrganizer
from dreamteams.application.preview_competitions.preview_competitions import (
    PreviewCompetitions,
    PreviewCompetitionsInput,
    PreviewCompetitionsList,
)
from dreamteams.application.publish_competition import CompetitionForm, CreatedCompetition, PublishCompetition
from dreamteams.application.submit_application import (
    ExploreCompetitions,
    ExploreCompetitionsInput,
    ExploreCompetitionsList,
)
from dreamteams.application.submit_application import ReadCompetition as ReadCompetitionAsParticipant
from dreamteams.application.update_my_competition import (
    ChangeCompetitionArchiveStatus,
    ChangeCompetitionArchiveStatusForm,
    RescheduleCompetition,
    RescheduleCompetitionForm,
    UpdateCompetitionGeneralInfo,
    UpdateCompetitionGeneralInfoForm,
)
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


@router.get("/explore")
async def explore_competitions(
    interactor: FromDishka[ExploreCompetitions],
    input_data: Annotated[ExploreCompetitionsInput, Query()],
) -> ExploreCompetitionsList:
    """Participant-facing explore endpoint with rich filters."""
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
    interactor: FromDishka[PublishCompetition],
    data: CompetitionForm,
) -> CreatedCompetition:
    """HTTP endpoint for creating a competition."""
    return await interactor.execute(data)


@router.get("/explore/{competition_id}")
async def read_competition_for_submission(
    interactor: FromDishka[ReadCompetitionAsParticipant],
    competition_id: CompetitionId,
) -> CompetitionModel:
    """Participant-facing endpoint for reading a single competition by ID."""
    return await interactor.execute(competition_id)


@router.get("/{competition_id}")
async def read_competition(
    interactor: FromDishka[ReadCompetitionAsOrganizer],
    competition_id: CompetitionId,
) -> CompetitionModel:
    """HTTP endpoint for reading a competition by ID."""
    return await interactor.execute(competition_id)


@router.patch("/{competition_id}/general-info")
async def update_competition_general_info(
    interactor: FromDishka[UpdateCompetitionGeneralInfo],
    competition_id: CompetitionId,
    data: UpdateCompetitionGeneralInfoForm,
) -> None:
    """HTTP endpoint for updating competition general information."""
    await interactor.execute(competition_id, data)


@router.patch("/{competition_id}/schedule")
async def reschedule_competition(
    interactor: FromDishka[RescheduleCompetition],
    competition_id: CompetitionId,
    data: RescheduleCompetitionForm,
) -> None:
    """HTTP endpoint for rescheduling a competition."""
    await interactor.execute(competition_id, data)


@router.patch("/{competition_id}/archive-status")
async def change_competition_archive_status(
    interactor: FromDishka[ChangeCompetitionArchiveStatus],
    competition_id: CompetitionId,
    data: ChangeCompetitionArchiveStatusForm,
) -> None:
    """HTTP endpoint for changing competition archive status."""
    await interactor.execute(competition_id, data)


@router.delete("/{competition_id}")
async def delete_competition(
    interactor: FromDishka[DeleteCompetition],
    competition_id: CompetitionId,
) -> None:
    """HTTP endpoint for deleting a competition."""
    await interactor.execute(competition_id)
