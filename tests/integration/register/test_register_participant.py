from faker import Faker

from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


async def test_register_as_participant(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test register as participant."""
    data = {**participant_form_factory.build().model_dump(mode="json")}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data)

    response.assert_status(200).ensure_content()
