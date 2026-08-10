import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.services import interview_service
from backend.app.schemas.interview import SessionOut
from backend.app.core.logging import get_logger
from backend.app.api.dependencies import get_current_user
from backend.app.db.models.candidate import Candidate

logger = get_logger("interview_routes", log_file="logs/interview_routes.log", level=logging.INFO)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/start", response_model=SessionOut)
def start_interview(num_questions: int = 5,db: Session = Depends(get_db),current_user: Candidate = Depends(get_current_user)):
    try:
        session = interview_service.create_session(db=db,
            candidate_id=current_user.id,num_questions=num_questions)
        return session
    except Exception as e:
        logger.error(f"Unexpected error {e}")


@router.get("/{session_id}", response_model=SessionOut)
def get_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    return interview_service.get_session(db, session_id)


@router.get("", response_model=List[SessionOut])
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    return interview_service.get_candidate_sessions(db, current_user.id)


@router.post("/{session_id}/abandon", response_model=SessionOut)
def abandon_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    return interview_service.abandon_session(db, session_id)