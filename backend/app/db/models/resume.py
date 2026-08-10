from sqlalchemy import ( Column,Integer,DateTime,Text,ForeignKey)
from backend.app.db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

class ResumeChunk(Base):
    __tablename__="resume_chunks"
    id=Column(Integer,primary_key=True,index=True)
    candidate_id=Column(Integer,ForeignKey("candidates.id",ondelete="CASCADE"),nullable=False)
    chunk_index  = Column(Integer, nullable=False) 
    chunk_text   = Column(Text, nullable=False)
    embedding    = Column(Vector(384), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    candidate = relationship("Candidate", back_populates="resume_chunks")