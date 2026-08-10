import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, Form, File, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.candidate import CandidateOut
from backend.app.services import candidate_service
from backend.app.core.logging import get_logger

logger = get_logger("candidate_routes", log_file="logs/candidate.log", level=logging.INFO)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    target_role: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        candidate = await candidate_service.register_candidate(
            db=db, name=name, email=email, password=password,
            target_role=target_role, resume=resume,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Candidate registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

    background_tasks.add_task(
        candidate_service.embed_resume_task, candidate.id, candidate.resume_text,db=db
    )
    logger.info(f"Candidate created: {candidate.email}")
    return candidate