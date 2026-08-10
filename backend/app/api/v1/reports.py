import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services import report_service
from backend.app.schemas.evaluation import ReportOut, FullReportOut
from backend.app.api.dependencies import get_current_user
from backend.app.db.models.candidate import Candidate
from backend.app.core.logging import get_logger

logger = get_logger("report_routes", log_file="logs/report_routes.log", level=logging.INFO)

router = APIRouter(prefix="/interviews", tags=["Reports"])


@router.get("/{session_id}/report", response_model=ReportOut)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    """
    Lightweight report — sirf overall summary (avg score, hiring recommendation, feedback).
    Dashboard/score-card view ke liye.
    """
    return report_service.get_report_for_candidate(db, session_id, current_user.id)


@router.get("/{session_id}/report/full", response_model=FullReportOut)
def get_full_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    """
    Poora detailed report — session + candidate + report + saare questions/answers/evaluations.
    Detailed review page ke liye (candidate apna poora interview transcript dekh sake).
    """
    return report_service.get_full_report_data(db, session_id, current_user.id)