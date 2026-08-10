import logging
from sqlalchemy.orm import Session

from backend.app.ml.pipelines.evaluation_pipeline import run_evaluation_pipeline
from backend.app.core.logging import get_logger

logger = get_logger("evaluation_worker", log_file="logs/evaluation_worker.log", level=logging.INFO)


def run_evaluation_job(db: Session, session_id: int, question_id: int, answer_id: int, transcript: str):
    try:
        logger.info(f"Evaluation job started — session={session_id}, question={question_id}")
        result = run_evaluation_pipeline(
            db=db,
            session_id=session_id,
            question_id=question_id,
            answer_id=answer_id,
            transcript=transcript
        )
        logger.info(f"Evaluation job completed — score={result.get('score')}")
    except Exception as e:
        logger.error(f"Evaluation job failed — session={session_id}: {e}")