from typing import Any, ClassVar, override

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.field import Field, FieldChoice, FieldType
from dreamteams.entities.application_form.fields import ApplicationFormFields


class FieldListType(TypeDecorator[ApplicationFormFields]):
    """SQLAlchemy TypeDecorator that serializes/deserializes ApplicationFormFields to/from JSONB."""

    impl: ClassVar[type[JSONB]] = JSONB  # type: ignore[misc,mutable-override]
    cache_ok: ClassVar[bool] = True  # type: ignore[misc,mutable-override]

    @override
    def process_bind_param(self, value: ApplicationFormFields | None, dialect: Any) -> list[dict[str, Any]] | None:
        if value is None:
            return None
        return [
            {
                "name": f.name,
                "type": f.type.value,
                "required": f.required,
                "choices": ([{"value": c.value} for c in f.choices] if f.choices is not None else None),
            }
            for f in value
        ]

    @override
    def process_result_value(self, value: list[dict[str, Any]] | None, dialect: Any) -> ApplicationFormFields | None:
        if value is None:
            return None
        fields = []
        for raw in value:
            choices = raw.get("choices")
            fields.append(
                Field(
                    name=raw["name"],
                    type=FieldType(raw["type"]),
                    required=raw["required"],
                    choices=(tuple(FieldChoice(value=c["value"]) for c in choices) if choices is not None else None),
                ),
            )
        return ApplicationFormFields(fields)


application_form_table = Table(
    "application_forms",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "competition_id",
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("fields", FieldListType, nullable=False),
    UniqueConstraint("competition_id", name="uq_application_forms_competition_id"),
)

mapper_registry.map_imperatively(
    ApplicationForm,
    application_form_table,
)
