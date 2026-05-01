from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from pydantic import BaseModel, Field

from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProvider
from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.register_user.register_participant import (
    CreatedParticipant,
    RegisterParticipant,
)
from dreamteams.application.register_user.register_participant import (
    ParticipantForm as InteractorParticipantForm,
)
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.user import ExperienceLevel

router = APIRouter(
    tags=["Participants"],
    route_class=DishkaRoute,
    prefix="/participants",
)


class ParticipantForm(BaseModel):
    """Participant form without email (email is provided by external identity service when available)."""

    full_name: str = Field(min_length=1, max_length=70)
    participant_type: ParticipantType
    age: int
    bio: str | None = Field(default=None, max_length=500)
    skills: list[ParticipantSkillForm] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    contacts: list[ParticipantContactForm] = Field(default_factory=list, max_length=15)


@router.post("/")
async def register_participant(
    interactor: FromDishka[RegisterParticipant],
    auth_user_idp: FromDishka[WebAuthUserIdProvider],
    data: ParticipantForm,
) -> CreatedParticipant:
    """HTTP endpoint for registering as ``Participant``."""
    return await interactor.execute(
        InteractorParticipantForm(
            full_name=data.full_name,
            participant_type=data.participant_type,
            age=data.age,
            bio=data.bio,
            skills=data.skills,
            experience_level=data.experience_level,
            contacts=data.contacts,
            email=auth_user_idp.get_auth_user_email_or_none(),
        ),
    )
