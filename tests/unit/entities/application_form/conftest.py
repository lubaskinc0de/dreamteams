from uuid import uuid4

from dreamteams.entities.application_form.entity import ApplicationForm, ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.field import Field, FieldChoice, FieldType
from dreamteams.entities.application_form.fields import ApplicationFormFields
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.user import Organizer
from dreamteams_common.clock import Clock
from tests.unit.conftest import NOW


def make_form(*fields: Field) -> ApplicationForm:
    """Build an ApplicationForm directly, bypassing the factory."""
    return ApplicationForm(
        id=uuid4(),
        competition_id=uuid4(),
        created_at=NOW,
        fields=ApplicationFormFields(list(fields)),
    )


def make_form_via_factory(
    organizer: Organizer,
    competition: Competition,
    clock: Clock,
    *fields: Field,
) -> ApplicationForm:
    """Create an ApplicationForm through the factory for a given competition."""
    return application_form_factory(
        data=ApplicationFormData(fields=ApplicationFormFields(list(fields))),
        competition=competition,
        organizer=organizer,
        clock=clock,
    )


STRING_FIELD = Field(name="bio", type=FieldType.STRING)
INT_FIELD = Field(name="age", type=FieldType.INT)
SELECT_FIELD = Field(
    name="size",
    type=FieldType.SELECT,
    choices=(
        FieldChoice(value="S"),
        FieldChoice(value="M"),
        FieldChoice(value="L"),
    ),
)
MULTISELECT_FIELD = Field(
    name="roles",
    type=FieldType.MULTISELECT,
    choices=(
        FieldChoice(value="frontend"),
        FieldChoice(value="backend"),
        FieldChoice(value="design"),
    ),
)
