from datetime import datetime

from adaptix.conversion import coercer, impl_converter
from pydantic import BaseModel

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId


class FieldChoiceModel(BaseModel):
    """A single selectable option in a SELECT or MULTISELECT field."""

    value: str
    label: str


class FieldModel(BaseModel):
    """A single field definition in an application form."""

    name: str
    label: str
    type: FieldType
    required: bool
    choices: list[FieldChoiceModel] | None


class ApplicationFormModel(BaseModel):
    """Full representation of an application form."""

    id: ApplicationFormId
    competition_id: CompetitionId
    created_at: datetime
    fields: list[FieldModel]


def _field_choice_to_model(choice: FieldChoice) -> FieldChoiceModel:
    return FieldChoiceModel(value=choice.value, label=choice.label)


def _field_to_model(field: Field) -> FieldModel:
    return FieldModel(
        name=field.name,
        label=field.label,
        type=field.type,
        required=field.required,
        choices=[_field_choice_to_model(c) for c in field.choices] if field.choices is not None else None,
    )


@impl_converter(recipe=[coercer(Field, FieldModel, func=_field_to_model)])
def to_application_form_model(form: ApplicationForm) -> ApplicationFormModel: ...  # type: ignore[empty-body]  # noqa: D103
