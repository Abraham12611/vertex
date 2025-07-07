import uuid
from sqlalchemy import Column, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.orm import relationship
import enum

class TaskStatus(enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)
    payload = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    agent = relationship("Agent", backref="tasks")