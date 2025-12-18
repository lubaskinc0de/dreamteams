from sqlalchemy import UUID, Column, ForeignKey, String, Table, Text

from posutochnik.adapters.db.models.base import mapper_registry
from posutochnik.entities.landlord import Landlord

landlord_table = Table(
    "landlord",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("landlord_name", String(150), nullable=False),
    Column("phone_number", String(100), nullable=False),
    Column("contact_email", Text, nullable=False),
)


mapper_registry.map_imperatively(
    Landlord,
    landlord_table,
)
