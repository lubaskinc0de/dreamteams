from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.manage_profile import ProfileModel, ReadProfile
from dreamteams.application.manage_profile.delete import DeleteProfile

router = APIRouter(
    tags=["Users"],
    route_class=DishkaRoute,
    prefix="/users",
)


@router.get("/me")
async def view_profile(
    interactor: FromDishka[ReadProfile],
) -> ProfileModel:
    """HTTP endpoint for viewing user profile."""
    return await interactor.execute()


@router.delete("/me")
async def delete_profile(
    interactor: FromDishka[DeleteProfile],
) -> None:
    """HTTP endpoint for deleting user profile."""
    await interactor.execute()
