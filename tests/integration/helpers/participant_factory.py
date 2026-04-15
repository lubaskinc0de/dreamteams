"""Factory for creating participant users via the API."""

from dataclasses import dataclass
from uuid import uuid4

from faker import Faker

from dreamteams.entities.common.vo.participant_type import ParticipantType
from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.models import ParticipantCreated


@dataclass
class ParticipantGateway:
    """Gateway for participant registration in tests."""

    api_client: ApiClient
    participant_form_factory: ParticipantFormFactory
    faker: Faker

    async def create(self, *, participant_type: ParticipantType | None = None) -> ParticipantCreated:
        """Register a fresh participant and return their credentials and form."""
        auth_id = str(uuid4())
        email = self.faker.email()
        kwargs = {} if participant_type is None else {"participant_type": participant_type}
        form = self.participant_form_factory.build(**kwargs)

        with self.api_client.authenticate(auth_user_id=auth_id, auth_user_email=email):
            participant = (
                (await self.api_client.register_participant(data=form.model_dump(mode="json")))
                .assert_status(200)
                .ensure_content()
            )

        return ParticipantCreated(auth_id=auth_id, email=email, form=form, created=participant)
