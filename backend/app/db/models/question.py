from sqlalchemy import ( Column,Integer,DateTime,Text,ForeignKey,Enum)
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

class QuestionType(str, enum.Enum):
    technical   = "technical"
    behavioral  = "behavioral"
    situational = "situational"

class Question(Base):
    __tablename__ = "questions"
 
    id      = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    q_index  = Column(Integer, nullable=False)          
    q_text    = Column(Text, nullable=False)
    q_type   = Column(Enum(QuestionType), default=QuestionType.technical)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session    = relationship("InterviewSession", back_populates="questions")
    answer     = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete")