from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional
from backend.app.schemas.interview import InterviewStatus

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
