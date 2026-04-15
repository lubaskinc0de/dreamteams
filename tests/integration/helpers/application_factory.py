"""Gateway for submitting and managing applications via the API."""

from __future__ import annotations

from dataclasses import dataclass

from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.submit_application import SubmitApplicationInput
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.competition_factory import CompetitionGateway
from tests.integration.helpers.models import CompetitionCreated
from tests.integration.helpers.participant_factory import ParticipantGateway


@dataclass
class ApplicationGateway:
    """Gateway for creating, reading and transitioning applications in tests."""

    api_client: ApiClient
    submit_application_input_factory: SubmitApplicationInputFactory
    participant_gateway: ParticipantGateway
    competition_gateway: CompetitionGateway

    async def submit(self, participant_auth_id: str, comp: CompetitionCreated) -> ApplicationId:
        """Submit an application to a competition on behalf of a participant."""
        data = self.submit_application_input_factory.build(
            domains=[comp.form.domains[0]],
            form_data=None,
        )

        with self.api_client.authenticate(auth_user_id=participant_auth_id):
            return (
                (await self.api_client.submit_application(comp.created.competition_id, data.model_dump(mode="json")))
                .assert_status(200)
                .ensure_content()
                .application_id
            )

    async def read_as_organizer(
        self,
        application_id: ApplicationId,
        organizer_auth_id: str,
    ) -> ApplicationModel:
        """Read a single application as the competition organizer."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            return (await self.api_client.read_application(application_id)).assert_status(200).ensure_content()

    async def read_as_participant(
        self,
        application_id: ApplicationId,
        participant_auth_id: str,
    ) -> ApplicationModel:
        """Read a single application as the participant who submitted it."""
        with self.api_client.authenticate(auth_user_id=participant_auth_id):
            return (await self.api_client.read_my_application(application_id)).assert_status(200).ensure_content()

    async def accept(self, application_id: ApplicationId, organizer_auth_id: str) -> None:
        """Accept a pending application as the competition organizer."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            (await self.api_client.accept_application(application_id)).assert_status(200)

    async def reject(self, application_id: ApplicationId, organizer_auth_id: str) -> None:
        """Reject a pending application as the competition organizer."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            (await self.api_client.reject_application(application_id)).assert_status(200)

    async def withdraw(self, application_id: ApplicationId, participant_auth_id: str) -> None:
        """Withdraw an application as the participant."""
        with self.api_client.authenticate(auth_user_id=participant_auth_id):
            (await self.api_client.withdraw_application(application_id)).assert_status(200)

    async def submit_to_n_competitions(
        self,
        n: int,
        owner_auth_id: str,
        participant_auth_id: str,
        *,
        auto_accept: bool = False,
    ) -> list[ApplicationModel]:
        """Create ``n`` fresh competitions, submit an application to each, and return participant-view models."""
        models: list[ApplicationModel] = []

        for _ in range(n):
            comp = await self.competition_gateway.create_active(owner_auth_id, auto_accept=auto_accept)
            app_id = await self.submit(participant_auth_id, comp)
            model = await self.read_as_participant(app_id, participant_auth_id)
            models.append(model)

        return models

    async def create_for_competition(
        self,
        n: int,
        competition_id: CompetitionId,
        submit_application_input: SubmitApplicationInput,
    ) -> list[ApplicationId]:
        """Create ``n`` fresh participants and have each submit an application to the competition."""
        submitted_ids: list[ApplicationId] = []

        for _ in range(n):
            participant = await self.participant_gateway.create()

            with self.api_client.authenticate(auth_user_id=participant.auth_id):
                app_id = (
                    (
                        await self.api_client.submit_application(
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

    async def create_mixed(
        self,
        application_ids: list[ApplicationId],
        organizer_auth_id: str,
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

        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            for app_id in application_ids[:num_accepted]:
                (await self.api_client.accept_application(app_id)).assert_status(200)
            for app_id in application_ids[num_accepted : num_accepted + num_rejected]:
                (await self.api_client.reject_application(app_id)).assert_status(200)

        return [await self.read_as_organizer(app_id, organizer_auth_id) for app_id in application_ids]
