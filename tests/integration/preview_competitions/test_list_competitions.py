
import pytest

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import USER_ID, create_competitions
from tests.integration.manage_competitions.helpers import create_competitions_list



