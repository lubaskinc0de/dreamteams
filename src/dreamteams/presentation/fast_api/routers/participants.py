from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.register.register_participant import (
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
    return await interactor.execute(
        ParticipantForm(
            full_name=data.full_name,
            bio=data.bio,
            skills=data.skills,
            experience_level=data.experience_level,
            preferred_domains=data.preferred_domains,
            contacts=data.contacts,
        ),
    )
