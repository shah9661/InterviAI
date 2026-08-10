import logging
from sqlalchemy.orm import Session

from backend.app.ml.pipelines.resume_pipeline import run_resume_pipeline
from backend.app.db.database import sessionLocal
from backend.app.core.logging import get_logger

logger = get_logger("resume_worker", log_file="logs/resume_worker.log", level=logging.INFO)


def run_resume_embedding_job(candidate_id: int, resume_text: str):
    db: Session = sessionLocal()
    try:
        logger.info(f"Resume embedding job started — candidate={candidate_id}")
        result = run_resume_pipeline(db, candidate_id, resume_text)

        if result.get("error"):
            logger.error(f"Resume embedding job failed — candidate={candidate_id}: {result['error']}")
        else:
            logger.info(
                f"Resume embedding job completed — candidate={candidate_id}, "
                f"chunks={result.get('chunk_count')}"
            )
    except Exception as e:
        logger.error(f"Unexpected error in resume embedding job — candidate={candidate_id}: {e}")
    finally:
        db.close()