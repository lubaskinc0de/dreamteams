"""Gateway for Participant entity construction in unit tests."""

from dataclasses import dataclass

from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.user import Participant, User, participant_factory
from dreamteams_common.clock import Clock
from tests.common.factory.entities.participant import ParticipantDataFactory
from tests.unit.helpers.user_gateway import UserGateway


@dataclass
class ParticipantGateway:
    """Gateway for building Participant entities via the domain factory."""

    participant_data_factory: type[ParticipantDataFactory]
    user_gateway: UserGateway
    clock: Clock

    def create(
        self,
        *,
        user: User | None = None,
        participant_type: ParticipantType | None = None,
    ) -> Participant:
        """Build a Participant through the domain ``participant_factory``."""
        u = user if user is not None else self.user_gateway.create()

        overrides: dict[str, object] = {}
        if participant_type is not None:
            overrides["participant_type"] = participant_type
        data = self.participant_data_factory.build(**overrides)

        return participant_factory(data=data, user=u, clock=self.clock)
