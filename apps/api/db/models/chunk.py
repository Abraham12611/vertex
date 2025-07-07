import uuid
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from db.base import Base
from sqlalchemy.orm import relationship

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_idx = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(VECTOR(1536), nullable=False)
    document = relationship("Document", back_populates="chunks")