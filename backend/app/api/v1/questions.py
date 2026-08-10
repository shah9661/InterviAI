import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models.question import Question
from backend.app.schemas.question import QuestionOut
from backend.app.ml.pipelines.question_pipeline import run_question_pipeline
from backend.app.core.logging import get_logger

logger = get_logger("question_routes", log_file="logs/question_routes.log", level=logging.INFO)

router = APIRouter(prefix="/sessions", tags=["Questions"])


@router.post("/{session_id}/generate-questions")
def generate_questions_endpoint(
    session_id: int,
    candidate_id: int,
    num_questions: int = 5,
    db: Session = Depends(get_db),
):
    result = run_question_pipeline(
        db=db,
        session_id=session_id,
        candidate_id=candidate_id,
        num_questions=num_questions
    )

    if result.get("error"):
        logger.error(f"Question generation failed for session {session_id}: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "message": f"{result['saved_count']} questions generated and saved",
        "saved_count": result["saved_count"]
    }


@router.get("/{session_id}/questions", response_model=List[QuestionOut])
def get_session_questions(session_id: int, db: Session = Depends(get_db)):
    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .order_by(Question.q_index)
        .all()
    )

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this session")

    return questions