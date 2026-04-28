from redis.asyncio import Redis

from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.manage_application_form.create_application_form import (
    ApplicationFormInput,
    FieldChoiceForm,
    FieldForm,
)
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
            FieldForm(
                name="roles",
                type=FieldType.MULTISELECT,
                required=False,
                choices=[
                    FieldChoiceForm(value="frontend"),
                    FieldChoiceForm(value="backend"),
                ],
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
        track=CompetitionTrackForm(name=competition.form.tracks[0].name),
        form_data={"motivation": f"candidate-{index}", "roles": ["frontend", "backend"]},
    )


async def prime_rate_limit(redis_url: str, user_id: UserId, max_attempts: int) -> None:
    """Set the exporter's rate-limit counter so the next process attempt fails."""
    redis: Redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        key = f"exporter:rl:{user_id}"
        await redis.set(key, str(max_attempts), ex=3600)
    finally:
        await redis.aclose()
