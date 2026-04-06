from uuid import uuid4

from dreamteams.entities.application_form.entity import ApplicationForm, ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.user import User
from tests.unit.conftest import NOW


def make_form(*fields: Field) -> ApplicationForm:
    """Build an ApplicationForm directly, bypassing the factory."""
    return ApplicationForm(
        id=uuid4(),
        competition_id=uuid4(),
        created_at=NOW,
        fields=list(fields),
    )


def make_form_via_factory(
    organizer_user: User,
    competition: Competition,
    clock: Clock,
    *fields: Field,
) -> ApplicationForm:
    """Create an ApplicationForm through the factory for a given competition."""
    return application_form_factory(
        data=ApplicationFormData(fields=list(fields)),
        competition=competition,
        user=organizer_user,
        clock=clock,
    )


STRING_FIELD = Field(name="bio", label="Short bio", type=FieldType.STRING)
INT_FIELD = Field(name="age", label="Your age", type=FieldType.INT)
SELECT_FIELD = Field(
    name="size",
    label="T-shirt size",
    type=FieldType.SELECT,
    choices=(
        FieldChoice(value="S", label="Small"),
        FieldChoice(value="M", label="Medium"),
        FieldChoice(value="L", label="Large"),
    ),
)
MULTISELECT_FIELD = Field(
    name="roles",
    label="Preferred roles",
    type=FieldType.MULTISELECT,
    choices=(
        FieldChoice(value="frontend", label="Frontend"),
        FieldChoice(value="backend", label="Backend"),
        FieldChoice(value="design", label="Design"),
    ),
)
