from sqlalchemy import ( Column, Float,Integer,DateTime,Text,ForeignKey)
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Answer(Base):
    __tablename__ = "answers"
 
    id          = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    transcript  = Column(Text, nullable=False)            
    duration_s  = Column(Float, nullable=True)            
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    question   = relationship("Question", back_populates="answer")
    evaluation = relationship("Evaluation", back_populates="answer", uselist=False, cascade="all, delete")