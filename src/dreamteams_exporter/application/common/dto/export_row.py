# ruff: noqa: RUF001 — the Russian column headers intentionally use Cyrillic letters.
from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class ExportRow:
    """Flattened read model written as a single row in the export.

    Field declaration order **is** the column order in the output file; keep it in sync
    with ``EXPORT_HEADERS`` below.
    """

    application_id: str
    competition_name: str
    domains: str
    status: str
    created_at: str
    form_data: str
    participant_id: str
    full_name: str
    bio: str
    participant_type: str
    age: str
    contacts: str


EXPORT_HEADERS: list[str] = [
    "ID заявки",
    "Название соревнования",
    "Направления",
    "Статус",
    "Дата подачи",
    "Данные формы",
    "ID участника",
    "ФИО",
    "О себе",
    "Тип участника",
    "Возраст",
    "Контакты",
]
