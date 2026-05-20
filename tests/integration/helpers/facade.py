"""Gateway facade — single fixture that tests inject to access all per-entity gateways."""

from dataclasses import dataclass

from tests.integration.helpers.admin_gateway import AdminGateway
from tests.integration.helpers.application_form_gateway import ApplicationFormGateway
from tests.integration.helpers.application_gateway import ApplicationGateway
from tests.integration.helpers.competition_gateway import CompetitionGateway
from tests.integration.helpers.organizer_gateway import OrganizerGateway
from tests.integration.helpers.participant_gateway import ParticipantGateway
from tests.integration.helpers.tag_gateway import TagGateway


@dataclass
class Gateway:
    """Facade providing access to all per-entity gateways."""

    admin: AdminGateway
    organizer: OrganizerGateway
    participant: ParticipantGateway
    competition: CompetitionGateway
    application: ApplicationGateway
    application_form: ApplicationFormGateway
    tags: TagGateway
