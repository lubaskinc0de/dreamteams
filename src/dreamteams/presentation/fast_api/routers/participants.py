from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.register_user.register_participant import (
    CreatedParticipant,
    ParticipantForm,
    RegisterParticipant,
)

router = APIRouter(
    tags=["Participants"],
    route_class=DishkaRoute,
    prefix="/participants",
)


@router.post("/")
async def register_participant(
    interactor: FromDishka[RegisterParticipant],
    data: ParticipantForm,
) -> CreatedParticipant:
    """HTTP endpoint for registering as ``Participant``."""
    return await interactor.execute(data)
