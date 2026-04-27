from datetime import datetime
from typing import cast

from adaptix.conversion import coercer, impl_converter
from pydantic import BaseModel, ConfigDict

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.vo.field import FieldType
from dreamteams.entities.application_form.vo.fields import ApplicationFormFields
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId


class FieldChoiceModel(BaseModel):
    """A single selectable option in a SELECT or MULTISELECT field."""

    model_config = ConfigDict(from_attributes=True)

    value: str


class FieldModel(BaseModel):
    """A single field definition in an application form."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    type: FieldType
    required: bool
    choices: list[FieldChoiceModel] | None


class ApplicationFormModel(BaseModel):
    """Full representation of an application form."""

    id: ApplicationFormId
    competition_id: CompetitionId
    created_at: datetime
    fields: list[FieldModel]


def _fields_to_models(fields: ApplicationFormFields) -> list[FieldModel]:
    return cast("list[FieldModel]", list(fields))


@impl_converter(
    recipe=[
        coercer(ApplicationFormFields, list[FieldModel], func=_fields_to_models),
    ],
)
def to_application_form_model(form: ApplicationForm) -> ApplicationFormModel: ...  # type: ignore[empty-body]  # noqa: D103
