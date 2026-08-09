from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,List


class SessionCreate(BaseModel):
    candidate_id: int
    num_questions: int = Field(default=5, ge=3, le=15)


class SessionOut(BaseModel):
    id: int
    candidate_id: int
    status: InterviewStatus
    num_questions: int
    total_score: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
class InterviewQuestion(BaseModel):
    q_text: str  = Field(description="The interview question")
    q_type: str  = Field(description="Type: technical | behavioral | situational")
    topic:  str  = Field(description="Topic this question covers e.g. Python, System Design")
 
class InterviewQuestionsOutput(BaseModel):
    questions: List[InterviewQuestion] = Field(description="List of interview questions")