import logging
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.db.models.interview import InterviewSession, InterviewStatus
from backend.app.db.models.candidate import Candidate
from backend.app.core.logging import get_logger

logger = get_logger("interview_service", log_file="logs/interview_service.log", level=logging.INFO)


def create_session(db: Session, candidate_id: int, num_questions: int = 5) -> InterviewSession:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        logger.warning(f"Session creation attempted for non-existent candidate: {candidate_id}")
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        session = InterviewSession(
            candidate_id=candidate_id,
            status=InterviewStatus.in_progress,
            num_questions=num_questions,
            started_at=datetime.utcnow(),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Interview session created — id={session.id}, candidate={candidate_id}")
        return session
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create session for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create interview session")


def get_session(db: Session, session_id: int) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


def get_candidate_sessions(db: Session, candidate_id: int) -> list[InterviewSession]:
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.candidate_id == candidate_id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )


def abandon_session(db: Session, session_id: int) -> InterviewSession:
    session = get_session(db, session_id)

    if session.status == InterviewStatus.completed:
        logger.warning(f"Attempted to abandon already completed session: {session_id}")
        raise HTTPException(status_code=400, detail="Session already completed")

    try:
        session.status = InterviewStatus.abandoned
        db.commit()
        db.refresh(session)
        logger.info(f"Session abandoned: {session_id}")
        return session
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to abandon session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session status")