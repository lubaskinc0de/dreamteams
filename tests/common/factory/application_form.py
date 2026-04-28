from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.manage_application_form.create_application_form import (
    ApplicationFormInput,
    FieldChoiceForm,
    FieldForm,
)
from dreamteams.entities.application_form.field import FieldType


def _field_forms_provider() -> list[FieldForm]:
    """Generate a valid, non-empty list of FieldForm objects with unique names."""
    random_ = ApplicationFormInputFactory.__random__
    faker = ApplicationFormInputFactory.__faker__

    candidates: list[FieldForm] = [
        FieldForm(
            name="bio",
            type=FieldType.STRING,
            required=True,
            choices=None,
        ),
        FieldForm(
            name="age",
            type=FieldType.INT,
            required=False,
            choices=None,
        ),
        FieldForm(
            name="size",
            type=FieldType.SELECT,
            required=True,
            choices=[
                FieldChoiceForm(value="s"),
                FieldChoiceForm(value="m"),
                FieldChoiceForm(value="l"),
            ],
        ),
        FieldForm(
            name="roles",
            type=FieldType.MULTISELECT,
            required=False,
            choices=[
                FieldChoiceForm(value="frontend"),
                FieldChoiceForm(value="backend"),
            ],
        ),
    ]

    count = random_.randint(1, len(candidates))
    chosen: list[FieldForm] = random_.sample(candidates, count)

    # Guarantee at least one field in case of unexpected filtering
    if not chosen:
        chosen = [
            FieldForm(
                name=faker.slug()[:20],
                type=FieldType.STRING,
                required=True,
                choices=None,
            ),
        ]

    return chosen


class ApplicationFormInputFactory(ModelFactory[ApplicationFormInput]):
    """Factory for ApplicationFormInput models."""

    __model__ = ApplicationFormInput

    fields = _field_forms_provider
