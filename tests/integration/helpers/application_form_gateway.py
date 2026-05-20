"""Gateway for creating and managing application forms via the API."""

from dataclasses import dataclass

from dreamteams.application.manage_application_form import ApplicationFormInput, CreatedApplicationForm
from dreamteams.entities.common.identifiers import CompetitionId
from tests.common.factory.application_form import ApplicationFormInputFactory
from tests.integration.api_client import ApiClient


@dataclass
class ApplicationFormGateway:
    """Gateway for creating, reading and deleting application forms in tests."""

    api_client: ApiClient
    application_form_input_factory: ApplicationFormInputFactory

    async def create(
        self,
        competition_id: CompetitionId,
        organizer_auth_id: str,
        form_input: ApplicationFormInput | None = None,
    ) -> CreatedApplicationForm:
        """Create an application form for a competition."""
        if form_input is None:
            form_input = self.application_form_input_factory.build()

        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            return (
                (await self.api_client.create_application_form(competition_id, form_input.model_dump(mode="json")))
                .assert_status(200)
                .ensure_content()
            )

    async def delete(self, competition_id: CompetitionId, organizer_auth_id: str) -> None:
        """Delete the application form for a competition."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            (await self.api_client.delete_application_form(competition_id)).assert_status(200)
