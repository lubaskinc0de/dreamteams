"""Use case: Manage Tags.

Actor: Admin
"""

from dreamteams.application.manage_tags.create import CompetitionTagInput, CreateCompetitionTag
from dreamteams.application.manage_tags.delete import DeleteCompetitionTag
from dreamteams.application.manage_tags.list import CompetitionTagsList, ListCompetitionTags, ListCompetitionTagsInput
from dreamteams.application.manage_tags.read import ReadCompetitionTag

__all__ = [
    "CompetitionTagInput",
    "CompetitionTagsList",
    "CreateCompetitionTag",
    "DeleteCompetitionTag",
    "ListCompetitionTags",
    "ListCompetitionTagsInput",
    "ReadCompetitionTag",
]
