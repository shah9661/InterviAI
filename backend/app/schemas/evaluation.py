from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class EvaluationOut(BaseModel):
    id: int
    answer_id: int
    score: int
    rating: EvaluationRating
    feedback: str
    strengths: Optional[List[str]]
    improvements: Optional[List[str]]
    evaluated_at: datetime

    class Config:
        from_attributes = True



class AnswerWithEval(BaseModel):
    answer: AnswerOut
    evaluation: Optional[EvaluationOut]


class ReportOut(BaseModel):
    id: int
    session_id: int
    avg_score: float
    total_questions: int
    answered: int
    strengths_summary: Optional[str]
    weaknesses_summary: Optional[str]
    hiring_recommendation: Optional[str]
    overall_feedback: Optional[str]
    generated_at: datetime

    class Config:
        from_attributes = True


class FullReportOut(BaseModel):
    session: SessionOut
    candidate: CandidateOut
    report: ReportOut
    questions: List[QuestionOut]
    answers_with_evals: List[AnswerWithEval]