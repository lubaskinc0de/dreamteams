from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from dreamteams.application.manage_applications import (
    AcceptApplication,
    ApplicationsList,
    ListApplicationsByCompetition,
    ReadApplication,
    RejectApplication,
)
from dreamteams.application.manage_my_applications import (
    ListMyApplications,
    ReadMyApplication,
    WithdrawApplication,
)
from dreamteams.application.manage_my_applications.list import ApplicationsList as MyApplicationsList
from dreamteams.application.manage_my_applications.read import ApplicationModel
from dreamteams.application.submit_application import CreatedApplication, SubmitApplication, SubmitApplicationInput
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId

competitions_router = APIRouter(
    tags=["Applications"],
    route_class=DishkaRoute,
    prefix="/competitions",
)

applications_router = APIRouter(
    tags=["Applications"],
    route_class=DishkaRoute,
    prefix="/applications",
)


@competitions_router.post("/{competition_id}/applications/")
async def submit_application(
    interactor: FromDishka[SubmitApplication],
    competition_id: CompetitionId,
    data: SubmitApplicationInput,
) -> CreatedApplication:
    """HTTP endpoint for submitting an application to a competition."""
    return await interactor.execute(competition_id, data)


@competitions_router.get("/{competition_id}/applications/")
async def list_applications_by_competition(
    interactor: FromDishka[ListApplicationsByCompetition],
    competition_id: CompetitionId,
    page: Annotated[int, Query(ge=1)] = 1,
) -> ApplicationsList:
    """HTTP endpoint for listing all applications submitted to a competition."""
    return await interactor.execute(competition_id, page)


@applications_router.get("/")
async def list_my_applications(
    interactor: FromDishka[ListMyApplications],
    page: Annotated[int, Query(ge=1)] = 1,
) -> MyApplicationsList:
    """HTTP endpoint for listing all applications submitted by the current participant."""
    return await interactor.execute(page)


@applications_router.get("/{application_id}/my/")
async def read_my_application(
    interactor: FromDishka[ReadMyApplication],
    application_id: ApplicationId,
) -> ApplicationModel:
    """HTTP endpoint for a participant to read their own application."""
    return await interactor.execute(application_id)


@applications_router.get("/{application_id}/")
async def read_application(
    interactor: FromDishka[ReadApplication],
    application_id: ApplicationId,
) -> ApplicationModel:
    """HTTP endpoint for an organizer to read an application."""
    return await interactor.execute(application_id)


@applications_router.delete("/{application_id}/")
async def withdraw_application(
    interactor: FromDishka[WithdrawApplication],
    application_id: ApplicationId,
) -> None:
    """HTTP endpoint for withdrawing (deleting) a pending application."""
    await interactor.execute(application_id)


@applications_router.post("/{application_id}/accept/")
async def accept_application(
    interactor: FromDishka[AcceptApplication],
    application_id: ApplicationId,
) -> None:
    """HTTP endpoint for accepting a pending application."""
    await interactor.execute(application_id)


@applications_router.post("/{application_id}/reject/")
async def reject_application(
    interactor: FromDishka[RejectApplication],
    application_id: ApplicationId,
) -> None:
    """HTTP endpoint for rejecting a pending application."""
    await interactor.execute(application_id)
