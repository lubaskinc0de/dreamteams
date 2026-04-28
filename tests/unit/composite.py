from datetime import datetime, timedelta
from typing import Any, overload
from zoneinfo import ZoneInfo

from hypothesis import strategies as st

from dreamteams.entities.application.entity import ApplicationData
from dreamteams.entities.application_form.entity import ApplicationForm, ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.application_form.vo.fields import ApplicationFormFields
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import (
    Competition,
    CompetitionData,
    UpdateCompetitionGeneralInfoData,
    competition_factory,
)
from dreamteams.entities.competition.milestone import Milestone, MilestoneData
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.competition.vo.tags import CompetitionTags
from dreamteams.entities.competition.vo.tracks import CompetitionTracks
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.participant.vo.participant_skills import ParticipantSkills
from dreamteams.entities.user import (
    ExperienceLevel,
    Organizer,
    Participant,
    ParticipantData,
    UpdateParticipantData,
    User,
    participant_factory,
)
from tests.unit.conftest import NOW_NAIVE


@st.composite
def ordered_pairs(draw: st.DrawFn) -> tuple[int, int]:
    """Ordered pairs (min, max) of integers."""
    n1 = draw(st.integers())
    n2 = draw(st.integers(min_value=n1))
    return (n1, n2)


@st.composite
def positive_ordered_pairs(draw: st.DrawFn) -> tuple[int, int]:
    """Ordered pairs (min, max) of positive integers."""
    n1 = draw(st.integers(min_value=1))
    n2 = draw(st.integers(min_value=n1))
    return (n1, n2)


@st.composite
def dt_past(draw: st.DrawFn, min_dt: datetime | None = None, max_dt: datetime | None = None) -> datetime:
    """Datetime in past."""
    max_value = min(max_dt, NOW_NAIVE - timedelta(minutes=1)) if max_dt else NOW_NAIVE - timedelta(minutes=1)

    if min_dt is None:
        return draw(
            st.datetimes(
                max_value=max_value,
                timezones=st.just(ZoneInfo("UTC")),
            ),
        )
    return draw(
        st.datetimes(
            min_value=min_dt,
            max_value=max_value,
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )


@st.composite
def dt_future(draw: st.DrawFn, min_dt: datetime | None = None) -> datetime:
    """Datetime in future."""
    if min_dt is not None:
        assert min_dt > NOW_NAIVE
    min_v = min_dt or NOW_NAIVE + timedelta(minutes=1)
    return draw(
        st.datetimes(
            min_value=min_v,
            max_value=min_v + timedelta(days=365 * 5),
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )


@st.composite
def valid_schedule_data(draw: st.DrawFn, min_dt: datetime | None = None) -> ScheduleData:
    """Valid schedule data with team formation period."""
    r_start = draw(dt_future(min_dt=min_dt))
    r_end = draw(dt_future(r_start.replace(tzinfo=None) + timedelta(minutes=1)))
    tf_start = draw(dt_future(r_end.replace(tzinfo=None) + timedelta(minutes=1)))
    tf_end = draw(dt_future(tf_start.replace(tzinfo=None) + timedelta(minutes=1)))
    return ScheduleData(
        registration_start=r_start,
        registration_end=r_end,
        team_formation_start=tf_start,
        team_formation_end=tf_end,
    )


@st.composite
def valid_schedule_data_no_team_formation(draw: st.DrawFn, min_dt: datetime | None = None) -> ScheduleData:
    """Valid schedule data without team formation period."""
    r_start = draw(dt_future(min_dt=min_dt))
    r_end = draw(dt_future(r_start.replace(tzinfo=None) + timedelta(minutes=1)))
    return ScheduleData(
        registration_start=r_start,
        registration_end=r_end,
        team_formation_start=None,
        team_formation_end=None,
    )


@st.composite
def past_schedule(draw: st.DrawFn) -> CompetitionSchedule:
    """CompetitionSchedule with team formation period with dates in past."""
    base_date = draw(dt_past(max_dt=NOW_NAIVE - timedelta(minutes=4)))

    return CompetitionSchedule(
        registration_start=base_date,
        registration_end=base_date + timedelta(minutes=1),
        team_formation_start=base_date + timedelta(minutes=2),
        team_formation_end=base_date + timedelta(minutes=3),
    )


@st.composite
def open_schedule(draw: st.DrawFn) -> CompetitionSchedule:
    """CompetitionSchedule with registration window currently open (started in past, ends in future)."""
    r_start = draw(dt_past())
    r_end = draw(dt_future())
    return CompetitionSchedule(
        registration_start=r_start,
        registration_end=r_end,
        team_formation_start=None,
        team_formation_end=None,
    )


@st.composite
def valid_text(draw: st.DrawFn) -> str:
    """Valid text with min_length = 1, contains only non-space characters."""
    return draw(st.text(st.characters(exclude_categories=("Zs", "Zl", "Zp", "Cc", "Cf", "Cs", "Co", "Cn")), min_size=1))


@st.composite
def milestone_data(draw: st.DrawFn) -> MilestoneData:
    """Valid milestone data."""
    return MilestoneData(
        title=draw(valid_text()),
        timestamp=draw(dt_future()),
        description=draw(st.one_of(st.none(), st.text(max_size=300))),
    )


@st.composite
def milestone(draw: st.DrawFn) -> Milestone:
    """Valid milestone."""
    return Milestone(
        title=draw(valid_text()),
        timestamp=draw(dt_future()),
        description=draw(st.one_of(st.none(), st.text(max_size=300))),
    )


@overload
def _deduplicate_milestones(milestones: None) -> None: ...
@overload
def _deduplicate_milestones(milestones: list[Milestone]) -> list[Milestone]: ...
@overload
def _deduplicate_milestones(milestones: list[MilestoneData]) -> list[MilestoneData]: ...
def _deduplicate_milestones(milestones: Any) -> Any:
    """Deduplicate milestones by timestamp."""
    if milestones is None:
        return None
    seen: set[datetime] = set()
    result = []
    for m in milestones:
        if m.timestamp not in seen:
            seen.add(m.timestamp)
            result.append(m)
    return result


@st.composite
def competition_tag(draw: st.DrawFn) -> CompetitionTag:
    """Valid competition tag."""
    return CompetitionTag(id=draw(st.uuids()), value=draw(valid_text()))


@st.composite
def competition_track(draw: st.DrawFn) -> CompetitionTrack:
    """Valid competition track."""
    return CompetitionTrack(name=draw(valid_text()))


@st.composite
def valid_competition_data(draw: st.DrawFn) -> CompetitionData:
    """Valid competition data."""
    max_participants = draw(st.integers(min_value=1, max_value=10_000))
    venue_format = draw(st.sampled_from(CompetitionFormat))

    has_teams = draw(st.booleans())
    if has_teams:
        min_team, max_team = draw(positive_ordered_pairs())
        team_size: TeamSizeRange | None = TeamSizeRange(min=min_team, max=max_team)
        schedule = draw(valid_schedule_data())
    else:
        team_size = None
        schedule = draw(valid_schedule_data_no_team_formation())

    return CompetitionData(
        title=draw(valid_text()),
        description=draw(valid_text()),
        schedule=schedule,
        participant_limits=ParticipantLimits(max=max_participants),
        tags=CompetitionTags(
            draw(
                st.lists(
                    competition_tag(),
                    max_size=5,
                    unique_by=(lambda tag: tag.id, lambda tag: tag.value.casefold()),
                ),
            ),
        ),
        tracks=CompetitionTracks(
            draw(
                st.lists(
                    competition_track(),
                    min_size=1,
                    max_size=5,
                    unique_by=lambda track: track.name.casefold(),
                ),
            ),
        ),
        venue=CompetitionVenue(
            format=venue_format,
            location=draw(valid_text())
            if venue_format in [CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID]
            else None,
        ),
        team_size=team_size,
        participant_type=draw(st.sampled_from(ParticipantType)),
        auto_accept=draw(st.booleans()),
        milestones=_deduplicate_milestones(draw(st.one_of(st.none(), st.lists(milestone_data(), max_size=5)))),
    )


@st.composite
def valid_competition(
    draw: st.DrawFn,
    organizer: Organizer,
    clock: Clock,
    *,
    is_archived: bool = True,
    is_open: bool = False,
    is_ended: bool = False,
) -> Competition:
    """Valid competition entity.

    By default mirrors ``competition_factory`` behaviour: ``is_archived=True`` with a future
    registration schedule.  Keyword flags override the schedule / archive state:

    - ``is_open=True``  — registration window is currently open (started in past, ends in future)
    - ``is_ended=True`` — registration window is in the past (already ended)
    - ``is_archived``   — controls ``Competition.is_archived`` (default True)

    ``is_open`` and ``is_ended`` are mutually exclusive.
    """
    data = draw(valid_competition_data())
    competition = competition_factory(data, organizer, clock)
    competition.is_archived = is_archived
    if is_open:
        competition.schedule = draw(open_schedule())
    elif is_ended:
        competition.schedule = draw(past_schedule())
    return competition


@st.composite
def valid_competition_general_info_data(draw: st.DrawFn) -> UpdateCompetitionGeneralInfoData:
    """Valid competition general-info update data."""
    max_participants = draw(st.integers(min_value=1, max_value=10_000))
    venue_format = draw(st.sampled_from(CompetitionFormat))

    milestones = draw(st.one_of(st.none(), st.lists(milestone(), max_size=5)))

    return UpdateCompetitionGeneralInfoData(
        title=draw(valid_text()),
        description=draw(valid_text()),
        participant_limits=ParticipantLimits(max=max_participants),
        tags=CompetitionTags(
            draw(
                st.lists(
                    competition_tag(),
                    max_size=5,
                    unique_by=(lambda tag: tag.id, lambda tag: tag.value.casefold()),
                ),
            ),
        ),
        tracks=CompetitionTracks(
            draw(
                st.lists(
                    competition_track(),
                    min_size=1,
                    max_size=5,
                    unique_by=lambda track: track.name.casefold(),
                ),
            ),
        ),
        venue=CompetitionVenue(
            format=venue_format,
            location=draw(valid_text())
            if venue_format in [CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID]
            else None,
        ),
        participant_type=draw(st.sampled_from(ParticipantType)),
        milestones=(CompetitionMilestones(_deduplicate_milestones(milestones)) if milestones is not None else None),
        auto_accept=draw(st.booleans()),
    )


@st.composite
def participant_skill_data(draw: st.DrawFn) -> ParticipantSkill:
    """Valid ParticipantSkill."""
    return ParticipantSkill(
        name=draw(valid_text()),
        level=draw(st.sampled_from(list(SkillLevel))),
    )


@st.composite
def participant_contact_data(draw: st.DrawFn) -> ParticipantContact:
    """Valid ParticipantContact."""
    return ParticipantContact(
        title=draw(valid_text()),
        value=draw(valid_text()),
    )


@st.composite
def valid_participant_data(draw: st.DrawFn) -> ParticipantData:
    """Valid participant data."""
    full_name = draw(valid_text())
    bio = draw(st.one_of(st.none(), valid_text()))

    skills = draw(st.lists(participant_skill_data(), min_size=0))
    skills_unique = list({s.name: s for s in skills}.values())

    experience_level = draw(st.one_of(st.none(), st.sampled_from(list(ExperienceLevel))))

    contacts = draw(st.lists(participant_contact_data(), min_size=0, unique_by=(lambda c: c.title, lambda c: c.value)))

    participant_type = draw(st.sampled_from([ParticipantType.SCHOOLCHILD, ParticipantType.STUDENT]))

    age = draw(st.integers(min_value=0, max_value=150).map(Age))

    return ParticipantData(
        full_name=full_name,
        bio=bio,
        skills=ParticipantSkills(skills_unique),
        experience_level=experience_level,
        contacts=ParticipantContacts(contacts),
        participant_type=participant_type,
        age=age,
    )


@st.composite
def valid_participant(draw: st.DrawFn, user: User, clock: Clock) -> Participant:
    """Valid participant entity."""
    data = draw(valid_participant_data())
    return participant_factory(
        data=data,
        user=user,
        clock=clock,
    )


@st.composite
def valid_participant_update_data(draw: st.DrawFn) -> UpdateParticipantData:
    """Valid participant update data."""
    full_name = draw(valid_text())
    bio = draw(st.one_of(st.none(), valid_text()))

    skills = draw(st.lists(participant_skill_data(), min_size=0))
    skills_unique = list({s.name: s for s in skills}.values())

    experience_level = draw(st.one_of(st.none(), st.sampled_from(list(ExperienceLevel))))

    contacts = draw(st.lists(participant_contact_data(), min_size=0, unique_by=(lambda c: c.title, lambda c: c.value)))

    participant_type = draw(st.sampled_from([ParticipantType.SCHOOLCHILD, ParticipantType.STUDENT]))

    age = draw(st.integers(min_value=0, max_value=150).map(Age))

    return UpdateParticipantData(
        full_name=full_name,
        bio=bio,
        skills=ParticipantSkills(skills_unique),
        experience_level=experience_level,
        contacts=ParticipantContacts(contacts),
        participant_type=participant_type,
        age=age,
    )


@st.composite
def valid_application_data(draw: st.DrawFn, tracks: list[CompetitionTrack] | None = None) -> ApplicationData:
    """Valid application data. If tracks are provided, draws one of them."""
    selected = draw(st.sampled_from(tracks)) if tracks is not None else draw(competition_track())
    return ApplicationData(track=selected)


@st.composite
def valid_field_choice(draw: st.DrawFn) -> FieldChoice:
    """Valid FieldChoice with non-blank value."""
    return FieldChoice(value=draw(valid_text()))


@st.composite
def valid_field(draw: st.DrawFn, field_type: FieldType | None = None) -> Field:
    """Valid Field. Generates choices for SELECT/MULTISELECT types."""
    ft = field_type if field_type is not None else draw(st.sampled_from(list(FieldType)))
    name = draw(valid_text())
    required = draw(st.booleans())
    if ft in (FieldType.SELECT, FieldType.MULTISELECT):
        choices = draw(
            st.lists(valid_field_choice(), min_size=1, max_size=5, unique_by=lambda c: c.value),
        )
        return Field(name=name, type=ft, required=required, choices=tuple(choices))
    return Field(name=name, type=ft, required=required)


@st.composite
def valid_application_form_data(draw: st.DrawFn, min_fields: int = 1) -> ApplicationFormData:
    """ApplicationFormData with at least min_fields uniquely-named fields."""
    fields = draw(
        st.lists(valid_field(), min_size=min_fields, max_size=5, unique_by=lambda f: f.name),
    )
    return ApplicationFormData(fields=ApplicationFormFields(fields))


@st.composite
def valid_application_form(
    draw: st.DrawFn,
    organizer: Organizer,
    clock: Clock,
    competition: Competition,
) -> ApplicationForm:
    """Valid ApplicationForm entity created via factory."""
    data = draw(valid_application_form_data())
    return application_form_factory(data=data, competition=competition, organizer=organizer, clock=clock)


@st.composite
def valid_form_data_for_form(draw: st.DrawFn, form: ApplicationForm) -> dict[str, Any]:
    """Valid form_data dict satisfying all fields in the given ApplicationForm."""
    result: dict[str, Any] = {}
    for field in form.fields:
        # optional fields are randomly included or skipped
        if not field.required and not draw(st.booleans()):
            continue
        if field.type == FieldType.STRING:
            result[field.name] = draw(valid_text())
        elif field.type == FieldType.INT:
            result[field.name] = draw(st.integers())
        elif field.type == FieldType.SELECT:
            assert field.choices is not None
            result[field.name] = draw(st.sampled_from(field.choices)).value
        elif field.type == FieldType.MULTISELECT:
            assert field.choices is not None
            chosen = draw(
                st.lists(st.sampled_from(field.choices), min_size=1, unique_by=lambda c: c.value),
            )
            result[field.name] = [c.value for c in chosen]
    return result
