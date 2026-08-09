from sqlalchemy import ( Column, Float,Integer,DateTime,ForeignKey,Enum)
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

class InterviewStatus(str, enum.Enum):
    pending    = "pending"
    in_progress = "in_progress"
    completed  = "completed"
    cancelled  = "cancelled"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id            = Column(Integer, primary_key=True, index=True)
    candidate_id  = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    status        = Column(Enum(InterviewStatus), default=InterviewStatus.pending, nullable=False)
    num_questions = Column(Integer, default=5)
    total_score   = Column(Float, nullable=True)     
    started_at    = Column(DateTime, nullable=True)    
    completed_at  = Column(DateTime, nullable=True)  
    created_at    = Column(DateTime, default=datetime.utcnow) 
    candidate = relationship("Candidate", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete")
