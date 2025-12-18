from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from posutochnik.application.register.landlord import CreatedLandlord, LandlordForm, RegisterLandlord

router = APIRouter(
    tags=["Landlords"],
    route_class=DishkaRoute,
    prefix="/landlords",
)


@router.post("/")
async def register_landlord(
    interactor: FromDishka[RegisterLandlord],
    data: LandlordForm,
) -> CreatedLandlord:
    """HTTP endpoint for registering as ``Landlord``."""
    return await interactor.execute(data)
