from collections.abc import Iterable

from dreamteams.entities.application_form.field import Field
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError


class ApplicationFormFields(list[Field]):
    """Validated collection of application form fields — must be non-empty with unique names."""

    def __init__(self, items: Iterable[Field] = ()) -> None:
        super().__init__(items)
        if not self:
            raise InvalidApplicationFormDataError(message="Application form must have at least one field")
        names = [f.name for f in self]
        if len(names) != len(set(names)):
            raise InvalidApplicationFormDataError(message="Application form fields must have unique names")
