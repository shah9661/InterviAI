from pydantic import BaseModel
from backend.app.db.models.question import QuestionType

class QuestionOut(BaseModel):
    id: int
    session_id: int
    q_index: int
    q_text: str
    q_type: QuestionType

    class Config:
        from_attributes = True