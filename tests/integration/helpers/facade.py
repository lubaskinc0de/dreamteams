"""Gateway facade — single fixture that tests inject to access all per-entity gateways."""

from dataclasses import dataclass

from tests.integration.helpers.admin_factory import AdminGateway
from tests.integration.helpers.application_factory import ApplicationGateway
from tests.integration.helpers.application_form_factory import ApplicationFormGateway
from tests.integration.helpers.competition_factory import CompetitionGateway
from tests.integration.helpers.organizer_factory import OrganizerGateway
from tests.integration.helpers.participant_factory import ParticipantGateway


@dataclass
class Gateway:
    """Facade providing access to all per-entity gateways."""

    admin: AdminGateway
    organizer: OrganizerGateway
    participant: ParticipantGateway
    competition: CompetitionGateway
    application: ApplicationGateway
    application_form: ApplicationFormGateway
