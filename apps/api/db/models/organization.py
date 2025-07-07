import uuid
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base
from sqlalchemy.orm import relationship

user_organization = Table(
    "user_organization",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True),
)

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    users = relationship("User", secondary=user_organization, back_populates="organizations")