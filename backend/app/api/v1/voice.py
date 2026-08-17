import logging

from fastapi import (APIRouter,UploadFile,File,Form,Depends,
    BackgroundTasks)
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services import answer_service
from backend.app.workers.voice_to_text import transcribe_audio
from backend.app.workers.evaluation_worker import run_evaluation_job
from backend.app.api.dependencies import get_current_user
from backend.app.db.models.candidate import Candidate
from backend.app.core.logging import get_logger


logger = get_logger("voice_routes",log_file="logs/voice_routes.log",
    level=logging.INFO)

router = APIRouter(prefix="/voice",tags=["Voice"])

@router.post("/submit")
async def submit_voice_answer(
    file: UploadFile = File(...),
    question_id: int = Form(...),
    duration_s: float = Form(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),):

    try:
        audio_bytes = await file.read()
        text = await transcribe_audio(
            filename=file.filename,
            audio_bytes=audio_bytes)

        answer = answer_service.save_answer(
            db=db,
            question_id=question_id,
            candidate_id=current_user.id,
            transcript=text,
            duration_s=duration_s
        )

        session_id = answer_service.get_session_id_for_question(
            db,question_id)

        background_tasks.add_task(run_evaluation_job,db,
            session_id,question_id,answer.id,
            text)
        return {
            "message": "Answer submitted, evaluation in progress",
            "answer_id": answer.id,
            "transcript": text
        }

    except Exception as e:
        logger.error(f"Voice answer failed: {e}")
        raise