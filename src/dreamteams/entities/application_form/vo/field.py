from dataclasses import dataclass
from enum import StrEnum, auto

from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError


class FieldType(StrEnum):
    """Data type of a single field in an ApplicationForm."""

    STRING = auto()
    INT = auto()
    SELECT = auto()
    MULTISELECT = auto()


@dataclass(frozen=True, slots=True)
class FieldChoice:
    """A single selectable option for SELECT or MULTISELECT fields."""

    value: str
    label: str

    def __post_init__(self) -> None:
        """Validate FieldChoice invariants."""
        if not self.value or self.value.isspace():
            raise InvalidApplicationFormDataError(message="Choice value must not be empty")
        if not self.label or self.label.isspace():
            raise InvalidApplicationFormDataError(message="Choice label must not be empty")


@dataclass(frozen=True, slots=True)
class Field:
    """A single input field in an ApplicationForm."""

    name: str
    label: str
    type: FieldType
    required: bool = True
    choices: tuple[FieldChoice, ...] | None = None

    def __post_init__(self) -> None:
        """Validate Field invariants."""
        if not self.name or self.name.isspace():
            raise InvalidApplicationFormDataError(message="Field name must not be empty")
        if not self.label or self.label.isspace():
            raise InvalidApplicationFormDataError(message="Field label must not be empty")

        if self.type in (FieldType.SELECT, FieldType.MULTISELECT):
            if not self.choices:
                raise InvalidApplicationFormDataError(
                    message=f"Field '{self.name}' of type {self.type} must have at least one choice",
                )
            values = [c.value for c in self.choices]
            if len(values) != len(set(values)):
                raise InvalidApplicationFormDataError(
                    message=f"Field '{self.name}' has duplicate choice values",
                )
        elif self.choices is not None:
            raise InvalidApplicationFormDataError(
                message=f"Field '{self.name}' of type {self.type} must not have choices",
            )
