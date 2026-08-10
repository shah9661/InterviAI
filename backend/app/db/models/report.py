from sqlalchemy import ( Column,Integer,DateTime,Text,ForeignKey,Float)
from backend.app.db.database import Base
from sqlalchemy.sql import func
class OverallReport(Base):
    """Final report after interview completion"""
    __tablename__ = "overall_reports"
 
    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), unique=True)
    avg_score       = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    answered        = Column(Integer, nullable=False)
    strengths_summary    = Column(Text, nullable=True)
    weaknesses_summary   = Column(Text, nullable=True)
    hiring_recommendation = Column(Text, nullable=True)   
    overall_feedback     = Column(Text, nullable=True)    
    generated_at    = Column(DateTime(timezone=True), server_default=func.now())