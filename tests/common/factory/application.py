from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.explore_competitions import SubmitApplicationInput
from dreamteams.entities.common.vo.domain import Domain


def _domains_provider() -> list[Domain]:
    """Generate a non-empty list of domains for an application."""
    random_ = SubmitApplicationInputFactory.__random__
    all_domains = list(Domain)
    count = random_.randint(1, len(all_domains))
    return random_.sample(all_domains, count)


class SubmitApplicationInputFactory(ModelFactory[SubmitApplicationInput]):
    """Factory for SubmitApplicationInput models.

    Generates random domain subsets. Set ``form_data`` explicitly when the competition
    has an ApplicationForm attached.
    """

    __model__ = SubmitApplicationInput

    domains = _domains_provider
