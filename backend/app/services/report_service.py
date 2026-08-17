import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.db.models.report import OverallReport
from backend.app.db.models.interview import InterviewSession
from backend.app.db.models.question import Question
from backend.app.db.models.answer import Answer
from backend.app.core.logging import get_logger

logger = get_logger("report_service", log_file="logs/report_service.log", level=logging.INFO)


def get_report_by_session(db: Session, session_id: int) -> OverallReport:
    report = db.query(OverallReport).filter(OverallReport.session_id == session_id).first()
    if not report:
        logger.warning(f"Report not found for session: {session_id}")
        raise HTTPException(status_code=404, detail="Report not found — interview may not be completed yet")
    return report


def get_report_for_candidate(db: Session, session_id: int, candidate_id: int) -> OverallReport:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.candidate_id != candidate_id:
        logger.warning(f"IDOR attempt — candidate {candidate_id} tried to access report for session {session_id}")
        raise HTTPException(status_code=403, detail="You don't have access to this report")

    return get_report_by_session(db, session_id)


def get_full_report_data(db: Session, session_id: int, candidate_id: int) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.candidate_id != candidate_id:
        logger.warning(f"IDOR attempt — candidate {candidate_id} tried to access session {session_id}")
        raise HTTPException(status_code=403, detail="You don't have access to this session")

    report = get_report_by_session(db, session_id)

    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .order_by(Question.q_index)
        .all()
    )

    answers_with_evals = []
    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        answers_with_evals.append({
            "answer": answer,
            "evaluation": answer.evaluation if answer else None
        })

    return {
        "session": session,
        "candidate": session.candidate,
        "report": report,
        "questions": questions,
        "answers_with_evals": answers_with_evals
    }