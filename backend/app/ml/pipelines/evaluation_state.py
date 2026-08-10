from typing import TypedDict, Optional, List


class EvaluationState(TypedDict):
    session_id: int
    question_id: int
    answer_id: int
    transcript: str

    candidate_name: str
    candidate_role: str
    question_text: str
    resume_context: str

    score: Optional[int]
    rating: Optional[str]
    feedback: Optional[str]
    strengths: Optional[List[str]]
    improvements: Optional[List[str]]

    all_answered: bool
    answered_count: int
    total_questions: int

    report_generated: bool
    error: Optional[str]