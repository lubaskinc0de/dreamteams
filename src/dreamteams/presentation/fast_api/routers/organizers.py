from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from pydantic import BaseModel, Field

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProvider
from dreamteams.application.common.phone_number import RussianPhoneNumber
from dreamteams.application.register.organizer import (
    CreatedOrganizer,
    RegisterOrganizer,
)
from dreamteams.application.register.organizer import (
    OrganizerForm as InteractorOrganizerForm,
)

router = APIRouter(
    tags=["Organizers"],
    route_class=DishkaRoute,
    prefix="/organizers",
)


class OrganizerForm(BaseModel):
    """Organizer form without email (email provided from external id service for web)."""

    organizer_name: str = Field(max_length=70)
    phone_number: RussianPhoneNumber


@router.post("/")
async def register_organizer(
    interactor: FromDishka[RegisterOrganizer],
    auth_user_idp: FromDishka[WebAuthUserIdProvider],
    data: OrganizerForm,
) -> CreatedOrganizer:
    """HTTP endpoint for registering as ``Organizer``."""
    return await interactor.execute(
        InteractorOrganizerForm(
            organizer_name=data.organizer_name,
            phone_number=data.phone_number,
            contact_email=auth_user_idp.get_auth_user_email(),
        ),
    )
