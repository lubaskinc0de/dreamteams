# ruff: noqa: RUF001
import json

from redis.asyncio import Redis

from dreamteams.application.common.dto.application import ApplicationModel
from dreamteams.application.manage_application_form.create import ApplicationFormInput, FieldForm
from dreamteams.application.submit_application import SubmitApplicationInput
from dreamteams.entities.application_form.vo.field import FieldType
from dreamteams_exporter.entities.common.identifiers import UserId
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.helpers.models import CompetitionCreated

AUTH_HEADER_NAME = "X-Auth-User"


def export_form() -> ApplicationFormInput:
    """Build a deterministic application form used by CSV export assertions."""
    return ApplicationFormInput(
        fields=[
            FieldForm(
                name="motivation",
                type=FieldType.STRING,
                required=True,
                choices=None,
            ),
        ],
    )


def build_submission_input(
    factory: SubmitApplicationInputFactory,
    competition: CompetitionCreated,
    *,
    index: int = 0,
) -> SubmitApplicationInput:
    """Build a deterministic submission payload for one participant."""
    return factory.build(
        domains=[competition.form.domains[0]],
        form_data={"motivation": f"candidate-{index}"},
    )


def expected_row(application: ApplicationModel) -> dict[str, str]:
    """Project main's application model into the CSV row shape."""
    return {
        "ID заявки": str(application.id),
        "Название соревнования": application.competition_name,
        "Направления": ", ".join(application.domains),
        "Статус": application.status.value,
        "Дата подачи": application.created_at.isoformat(),
        "Данные формы": json.dumps(application.form_data, ensure_ascii=False)
        if application.form_data is not None
        else "",
        "ID участника": str(application.participant.id),
        "ФИО": application.participant.full_name,
        "О себе": application.participant.bio or "",
        "Тип участника": application.participant.participant_type,
        "Возраст": str(application.participant.age),
        "Контакты": ", ".join(f"{c.title}: {c.url}" for c in application.participant.contacts),
    }


async def prime_rate_limit(redis_url: str, user_id: UserId, max_attempts: int) -> None:
    """Set the exporter's rate-limit counter so the next process attempt fails."""
    redis: Redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        key = f"exporter:rl:{user_id}"
        await redis.set(key, str(max_attempts), ex=3600)
    finally:
        await redis.aclose()
