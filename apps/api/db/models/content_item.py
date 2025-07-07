import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base

class ContentItem(Base):
    __tablename__ = "content_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    markdown = Column(Text, nullable=False)
    html = Column(Text, nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
