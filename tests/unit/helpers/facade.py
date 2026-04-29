"""Gateway facade — single fixture tests inject to access all per-entity gateways."""

from dataclasses import dataclass

from tests.unit.helpers.organizer_gateway import OrganizerGateway
from tests.unit.helpers.organizer_invite_gateway import OrganizerInviteGateway
from tests.unit.helpers.participant_gateway import ParticipantGateway
from tests.unit.helpers.user_gateway import UserGateway


@dataclass
class Gateway:
    """Facade providing access to all per-entity unit-test gateways."""

    user: UserGateway
    organizer: OrganizerGateway
    participant: ParticipantGateway
    organizer_invite: OrganizerInviteGateway
