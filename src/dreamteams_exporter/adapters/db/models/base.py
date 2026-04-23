from sqlalchemy import MetaData
from sqlalchemy.orm import registry

from dreamteams_exporter.adapters.db.config import EXPORTER_SCHEMA

mapper_registry = registry(metadata=MetaData(schema=EXPORTER_SCHEMA))
"""SQLAlchemy mapper registry scoped to the exporter schema."""
