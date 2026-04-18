import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application_form import ApplicationFormAlreadyExistsError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.application_form.entity import ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.vo.field import Field as DomainField
from dreamteams.entities.application_form.vo.field import FieldChoice, FieldType
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class FieldChoiceForm(BaseModel):
    """A single selectable option for SELECT or MULTISELECT fields."""

    value: str
    label: str


class FieldForm(BaseModel):
    """A single input field definition."""

    name: str
    label: str
    type: FieldType
    required: bool = True
    choices: list[FieldChoiceForm] | None = None


class ApplicationFormInput(BaseModel):
    """Request body for creating an application form."""

    fields: list[FieldForm]


class CreatedApplicationForm(BaseModel):
    """Response model containing the identifier of a newly created ApplicationForm."""

    application_form_id: ApplicationFormId


@interactor
class CreateApplicationForm:
    """Interactor for creating an application form for a competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    application_form_gateway: ApplicationFormGateway
    clock: Clock
    metrics: MetricsGateway

    async def execute(self, competition_id: CompetitionId, data: ApplicationFormInput) -> CreatedApplicationForm:
        """Create a new ApplicationForm and attach it to a competition."""
        user_id = await self.idp.get_user_id()
        logger.debug("Creating application form", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        existing = await self.application_form_gateway.get_by_competition_id(competition_id)
        if existing is not None:
            logger.warning(
                "Application form already exists",
                competition_id=competition_id,
                user_id=user_id,
            )
            raise ApplicationFormAlreadyExistsError

        domain_fields = [
            DomainField(
                name=f.name,
                label=f.label,
                type=f.type,
                required=f.required,
                choices=(
                    tuple(FieldChoice(value=c.value, label=c.label) for c in f.choices)
                    if f.choices is not None
                    else None
                ),
            )
            for f in data.fields
        ]

        form = application_form_factory(
            data=ApplicationFormData(fields=domain_fields),
            competition=competition,
            organizer=organizer,
            clock=self.clock,
        )

        self.uow.add(form)
        await self.uow.commit()

        self.metrics.record_application_form_created()
        logger.info("Application form created", form_id=form.id, competition_id=competition_id)
        return CreatedApplicationForm(application_form_id=form.id)
