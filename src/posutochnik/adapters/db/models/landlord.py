from sqlalchemy import UUID, Column, ForeignKey, Table
from sqlalchemy.orm import relationship

from posutochnik.adapters.db.models.base import mapper_registry
from posutochnik.entities.landlord import Landlord

landlord_table = Table(
    "landlord",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
)


mapper_registry.map_imperatively(
    Landlord,
    landlord_table,
    properties={
        "user": relationship("User", lazy="selectin"),
    },
)
