from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from pydantic import BaseModel, Field

from posutochnik.adapters.auth.idp.auth_user import WebAuthUserIdProvider
from posutochnik.application.common.phone_number import RussianPhoneNumber
from posutochnik.application.register.landlord import (
    CreatedLandlord,
    RegisterLandlord,
)
from posutochnik.application.register.landlord import (
    LandlordForm as InteractorLandlordForm,
)

router = APIRouter(
    tags=["Landlords"],
    route_class=DishkaRoute,
    prefix="/landlords",
)


class LandlordForm(BaseModel):
    """Landlord form without email (email provided from external id service for web)."""

    landlord_name: str = Field(max_length=70)
    phone_number: RussianPhoneNumber


@router.post("/")
async def register_landlord(
    interactor: FromDishka[RegisterLandlord],
    auth_user_idp: FromDishka[WebAuthUserIdProvider],
    data: LandlordForm,
) -> CreatedLandlord:
    """HTTP endpoint for registering as ``Landlord``."""
    return await interactor.execute(
        InteractorLandlordForm(
            landlord_name=data.landlord_name,
            phone_number=data.phone_number,
            contact_email=auth_user_idp.get_auth_user_email(),
        ),
    )
