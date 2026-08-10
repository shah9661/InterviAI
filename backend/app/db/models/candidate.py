from sqlalchemy import ( Column, String,Integer,DateTime,Text,ForeignKey)
from backend.app.db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Candidate(Base):
    __tablename__ ="candidates"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255),nullable=False)
    email=Column(String(255),nullable=False,unique=True,index=True)
    password_hash = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=False)
    resume_text = Column(Text, nullable=False)
    created_at=Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    resume_chunks = relationship("ResumeChunk", back_populates="candidate", cascade="all, delete")
    sessions      = relationship("InterviewSession", back_populates="candidate", cascade="all, delete")
    