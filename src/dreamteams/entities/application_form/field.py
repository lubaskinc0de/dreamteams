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


@dataclass(frozen=True, slots=True)
class Field:
    """A single input field in an ApplicationForm."""

    name: str
    type: FieldType
    required: bool = True
    choices: tuple[FieldChoice, ...] | None = None

    def __post_init__(self) -> None:
        """Validate Field type/choices invariants."""
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
