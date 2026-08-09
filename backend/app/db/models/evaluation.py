from sqlalchemy import ( Column, JSON,Enum,Integer,DateTime,Text,ForeignKey)
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

class EvaluationRating(str, enum.Enum):
    excellent = "Excellent"
    good      = "Good"
    average   = "Average"
    poor      = "Poor"

class Evaluation(Base):
    __tablename__ = "evaluations"
 
    id          = Column(Integer, primary_key=True, index=True)
    answer_id   = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    score       = Column(Integer, nullable=False)        
    rating      = Column(Enum(EvaluationRating), nullable=False)
    feedback    = Column(Text, nullable=False)            
    strengths   = Column(JSON, nullable=True)              
    improvements = Column(JSON, nullable=True)             
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    answer = relationship("Answer", back_populates="evaluation")