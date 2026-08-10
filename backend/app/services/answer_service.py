import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.db.models.answer import Answer
from backend.app.db.models.question import Question
from backend.app.db.models.interview import InterviewSession
from backend.app.core.logging import get_logger

logger = get_logger("answer_service", log_file="logs/answer_service.log", level=logging.INFO)


def save_answer(
    db: Session,
    question_id: int,
    candidate_id: int,
    transcript: str,
    duration_s: float = None
) -> Answer:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        logger.warning(f"Answer submit attempt for non-existent question: {question_id}")
        raise HTTPException(status_code=404, detail="Question not found")

    session = db.query(InterviewSession).filter(InterviewSession.id == question.session_id).first()
    if not session or session.candidate_id != candidate_id:
        logger.warning(f"IDOR attempt — candidate {candidate_id} tried to answer question {question_id}")
        raise HTTPException(status_code=403, detail="You don't have access to this question")

    existing = db.query(Answer).filter(Answer.question_id == question_id).first()
    if existing:
        logger.warning(f"Duplicate answer attempt for question: {question_id}")
        raise HTTPException(status_code=400, detail="This question has already been answered")

    try:
        answer = Answer(
            question_id=question_id,
            transcript=transcript,
            duration_s=duration_s
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        logger.info(f"Answer saved — question_id={question_id}, answer_id={answer.id}")
        return answer
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to save answer for question {question_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save answer")


def get_session_id_for_question(db: Session, question_id: int) -> int:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question.session_id