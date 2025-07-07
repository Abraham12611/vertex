import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String, nullable=False)
    text = Column(Text, nullable=True)
    embedding = Column(VECTOR(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    chunks = relationship("Chunk", back_populates="document")