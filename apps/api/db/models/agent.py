import uuid
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.base import Base
from sqlalchemy.orm import relationship
import enum

class AgentType(enum.Enum):
    strategy = "strategy"
    content = "content"
    community = "community"
    analytics = "analytics"

class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    type = Column(Enum(AgentType), nullable=False)
    config = Column(JSONB, nullable=True)
    status = Column(String, nullable=False, default="offline")
    project = relationship("Project", backref="agents")