from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class AnswerCreate(BaseModel):
    transcript: str = Field(..., min_length=1)
    duration_s: Optional[float] = None


class AnswerOut(BaseModel):
    id: int
    question_id: int
    transcript: str
    duration_s: Optional[float]
    submitted_at: datetime

    class Config:
        from_attributes = True