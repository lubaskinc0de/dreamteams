from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.application.manage_my_applications import ApplicationModel, ApplicationsList
from dreamteams.application.manage_my_applications.list import PAGE_SIZE
from dreamteams.entities.common.identifiers import ApplicationId
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import activate_competition
from tests.integration.constants import PARTICIPANT_USER_ID, USER_ID


def create_my_applications_list(
    applications: list[ApplicationModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> ApplicationsList:
    """Build paginated ``ApplicationsList`` from ``list[ApplicationModel]`` sorted by ``created_at`` descending."""
    sorted_items = sorted(applications, key=lambda a: a.created_at, reverse=True)
    start = (page - 1) * page_size
    paginated = sorted_items[start : start + page_size]
    return ApplicationsList(items=paginated, total=len(applications), page=page)


async def create_competition_and_submit(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    submit_application_input_factory: SubmitApplicationInputFactory,
    session: AsyncSession,
) -> ApplicationId:
    """Create one active competition as USER_ID organizer and have PARTICIPANT_USER_ID participant submit to it."""
    comp_form = competition_form_factory.build(auto_accept=False)
    with api_client.authenticate(auth_user_id=USER_ID):
        competition_id = (
            (await api_client.create_competition(comp_form.model_dump(mode="json")))
            .assert_status(200)
            .ensure_content()
            .competition_id
        )

    await activate_competition(
        api_client,
        session,
        update_competition_form_factory,
        competition_id,
        domains=comp_form.domains,
        auto_accept=False,
    )

    submit_input = submit_application_input_factory.build(
        domains=[comp_form.domains[0]],
        form_data=None,
    )
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        return (
            (await api_client.submit_application(competition_id, submit_input.model_dump(mode="json")))
            .assert_status(200)
            .ensure_content()
            .application_id
        )
