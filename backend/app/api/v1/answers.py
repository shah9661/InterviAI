# import logging
# from fastapi import APIRouter, Depends, BackgroundTasks
# from sqlalchemy.orm import Session
# from backend.app.schemas.answer import AnswerSubmit

# from backend.app.db.database import get_db
# from backend.app.services import answer_service
# from backend.app.workers.evaluation_worker import run_evaluation_job
# from backend.app.api.dependencies import get_current_user
# from backend.app.db.models.candidate import Candidate
# from backend.app.core.logging import get_logger

# logger = get_logger("answer_routes", log_file="logs/answer_routes.log", level=logging.INFO)

# router = APIRouter(prefix="/answers", tags=["Answers"])

# @router.post("/submit")
# def submit_answer(
#     payload: AnswerSubmit,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     current_user: Candidate = Depends(get_current_user),
# ):
#     answer = answer_service.save_answer(
#         db=db,
#         question_id=payload.question_id,
#         candidate_id=current_user.id,
#         transcript=payload.transcript,
#         duration_s=payload.duration_s
#     )

#     session_id = answer_service.get_session_id_for_question(db, payload.question_id)

#     background_tasks.add_task(
#         run_evaluation_job,
#         db,
#         session_id,
#         payload.question_id,
#         answer.id,
#         payload.transcript
#     )

#     logger.info(f"Answer submitted, evaluation queued — answer_id={answer.id}")
#     return {
#         "message": "Answer submitted, evaluation in progress",
#         "answer_id": answer.id
#     }