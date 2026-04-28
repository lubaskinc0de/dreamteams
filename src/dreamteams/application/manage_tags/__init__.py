"""Use case: Manage Tags.

Actor: Admin
Admin maintains the competition tag catalog.
"""

from dreamteams.application.manage_tags.create_tag import CompetitionTagInput, CreateCompetitionTag
from dreamteams.application.manage_tags.delete_tag import DeleteCompetitionTag
from dreamteams.application.manage_tags.list_tags import (
    CompetitionTagsList,
    ListCompetitionTags,
    ListCompetitionTagsInput,
)
from dreamteams.application.manage_tags.read_tag import ReadCompetitionTag

__all__ = [
    "CompetitionTagInput",
    "CompetitionTagsList",
    "CreateCompetitionTag",
    "DeleteCompetitionTag",
    "ListCompetitionTags",
    "ListCompetitionTagsInput",
    "ReadCompetitionTag",
]
