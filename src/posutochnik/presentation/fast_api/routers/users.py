from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from posutochnik.application.view_profile.interactor import ProfileModel, ViewProfile

router = APIRouter(
    tags=["Users"],
    route_class=DishkaRoute,
    prefix="/users",
)


@router.get("/me")
async def view_profile(
    interactor: FromDishka[ViewProfile],
) -> ProfileModel:
    """HTTP endpoint for viewing user profile."""
    return await interactor.execute()
