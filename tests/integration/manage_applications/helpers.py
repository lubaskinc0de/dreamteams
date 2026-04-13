from uuid import uuid4

from faker import Faker

from dreamteams.application.manage_applications import ApplicationsList
from dreamteams.application.manage_applications.list import PAGE_SIZE
from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.submit_application import SubmitApplicationInput
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId
from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


def create_applications_list(
    applications: list[ApplicationModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> ApplicationsList:
    """Build paginated ``ApplicationsList`` from ``list[ApplicationModel]`` sorted by ``created_at`` descending."""
    sorted_items = sorted(applications, key=lambda a: a.created_at, reverse=True)
    start = (page - 1) * page_size
    paginated = sorted_items[start : start + page_size]
    return ApplicationsList(items=paginated, total=len(applications), page=page)


async def read_application_as_organizer(api_client: ApiClient, application_id: ApplicationId) -> ApplicationModel:
    """Read a single application as the competition organizer (USER_ID)."""
    with api_client.authenticate(auth_user_id=USER_ID):
        return (await api_client.read_application(application_id)).assert_status(200).ensure_content()


async def create_mixed_applications(
    api_client: ApiClient,
    application_ids: list[ApplicationId],
) -> list[ApplicationModel]:
    """Transition applications to mixed statuses and return their current models.

    Distribution:
    - n == 0: empty
    - n == 1: leave as PENDING
    - n == 2: first is ACCEPTED, second is REJECTED
    - n >= 3: first third ACCEPTED, next third REJECTED, remainder PENDING
    """
    _pair_size = 2
    n = len(application_ids)
    if n == 0:
        return []

    if n == _pair_size:
        num_accepted, num_rejected = 1, 1
    else:
        num_accepted = n // 3
        num_rejected = n // 3

    with api_client.authenticate(auth_user_id=USER_ID):
        for app_id in application_ids[:num_accepted]:
            (await api_client.accept_application(app_id)).assert_status(200)
        for app_id in application_ids[num_accepted : num_accepted + num_rejected]:
            (await api_client.reject_application(app_id)).assert_status(200)

    return [await read_application_as_organizer(api_client, app_id) for app_id in application_ids]


async def create_applications_for_competition(
    num_applications: int,
    api_client: ApiClient,
    competition_id: CompetitionId,
    submit_application_input: SubmitApplicationInput,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> list[ApplicationId]:
    """Register ``num_applications`` fresh participants and have each submit an application."""
    submitted_ids: list[ApplicationId] = []
    for _ in range(num_applications):
        participant_user_id = str(uuid4())
        form = participant_form_factory.build()
        with api_client.authenticate(auth_user_id=participant_user_id, auth_user_email=faker.email()):
            (await api_client.register_participant(data=form.model_dump(mode="json"))).assert_status(200)
        with api_client.authenticate(auth_user_id=participant_user_id):
            app_id = (
                (
                    await api_client.submit_application(
                        competition_id,
                        submit_application_input.model_dump(mode="json"),
                    )
                )
                .assert_status(200)
                .ensure_content()
                .application_id
            )
            submitted_ids.append(app_id)
    return submitted_ids
