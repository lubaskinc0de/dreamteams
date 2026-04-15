from dreamteams.entities.application.entity import Application, ApplicationData, application_factory
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.errors.application import (
    CompetitionNotActiveError,
    ParticipantLimitsExceededError,
    ParticipantTypeMismatchError,
)
from dreamteams.entities.user import User


def submit_application(  # noqa: PLR0913
    data: ApplicationData,
    user: User,
    competition: Competition,
    accepted_count: int,
    clock: Clock,
    form: ApplicationForm | None = None,
) -> Application:
    """Domain service: validate submission eligibility and create an Application.

    Checks (in order):
    1. Competition must not be archived.
    2. Registration window must be currently open.
    3. Participant type must satisfy the competition's requirement.
    4. Accepted count must be strictly below participant_limits.max.

    Delegates to ``application_factory`` for entity-level validation
    (domains, form_data, participant access check, auto_accept status).
    """
    if competition.is_archived:
        raise CompetitionNotActiveError(message="Competition is archived and not accepting applications")

    now = clock.now()
    schedule = competition.schedule
    if now < schedule.registration_start or now > schedule.registration_end:
        raise CompetitionNotActiveError(message="Competition registration is not currently open")

    if user.participant is not None and competition.participant_type not in {
        ParticipantType.ANY,
        user.participant.participant_type,
    }:
        raise ParticipantTypeMismatchError

    if accepted_count >= competition.participant_limits.max:
        raise ParticipantLimitsExceededError

    return application_factory(data=data, user=user, competition=competition, clock=clock, form=form)
