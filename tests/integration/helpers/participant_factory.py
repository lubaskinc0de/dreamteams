"""Factory for creating participant users via the API."""

from dataclasses import dataclass
from uuid import uuid4

from faker import Faker

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.entities.common.participant_type import ParticipantType
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
        form = (
            self.participant_form_factory.build(participant_type=participant_type)
            if participant_type is not None
            else self.participant_form_factory.build()
        )

        with self.api_client.authenticate(auth_user_id=auth_id, auth_user_email=email):
            participant = (
                (await self.api_client.register_participant(data=form.model_dump(mode="json", exclude={"email"})))
                .assert_status(200)
                .ensure_content()
            )

        created_form = form.model_copy(
            update={
                "email": email,
                "contacts": [*form.contacts, ParticipantContactForm(title="Email", value=email)],
            },
        )
        return ParticipantCreated(auth_id=auth_id, email=email, form=created_form, created=participant)
