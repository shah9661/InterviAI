from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import enum


class InterviewStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"

class SessionCreate(BaseModel):
    candidate_id: int
    num_questions: int = Field(default=5, ge=3, le=15)


class SessionOut(BaseModel):
    id: int
    candidate_id: int
    status: InterviewStatus
    num_questions: int
    total_score: float | None
    started_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True
        
class InterviewQuestion(BaseModel):
    q_text: str  = Field(description="The interview question")
    q_type: str  = Field(description="Type: technical | behavioral | situational")
    topic:  str  = Field(description="Topic this question covers e.g. Python, System Design")
 
class InterviewQuestionsOutput(BaseModel):
    questions: List[InterviewQuestion] = Field(description="List of interview questions")