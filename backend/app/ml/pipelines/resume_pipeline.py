import logging
from typing import TypedDict, Optional
from sqlalchemy.orm import Session

from backend.app.ml.rag.context_builder import store_resume_vector
from backend.app.db.models.candidate import Candidate
from backend.app.core.logging import get_logger

logger = get_logger("resume_pipeline", log_file="logs/resume_pipeline.log", level=logging.INFO)


class ResumeState(TypedDict):
    candidate_id: int
    resume_text: str

    chunk_count: Optional[int]
    embedding_done: bool

    error: Optional[str]


def chunk_and_embed_node(state: ResumeState, db: Session) -> ResumeState:
    try:
        candidate = db.query(Candidate).filter(Candidate.id == state["candidate_id"]).first()
        if not candidate:
            logger.error(f"Candidate not found: {state['candidate_id']}")
            return {**state, "error": "Candidate not found"}

        resume_text = state["resume_text"]
        if not resume_text or not resume_text.strip():
            logger.warning(f"Empty resume text for candidate {state['candidate_id']}")
            return {**state, "error": "Resume text is empty"}

        logger.info(f"Chunking + embedding resume for candidate {state['candidate_id']}")
        chunk_count = store_resume_vector(
            db=db,
            candidate_id=state["candidate_id"],
            resume_text=resume_text
        )

        return {
            **state,
            "chunk_count": chunk_count,
            "embedding_done": True,
            "error": None
        }

    except Exception as e:
        logger.error(f"[chunk_and_embed_node] Error for candidate {state['candidate_id']}: {e}")
        return {
            **state,
            "chunk_count": 0,
            "embedding_done": False,
            "error": str(e)
        }


def run_resume_pipeline(db: Session, candidate_id: int, resume_text: str) -> dict:
    logger.info(f"Starting resume pipeline for candidate {candidate_id}")

    initial_state: ResumeState = {
        "candidate_id": candidate_id,
        "resume_text": resume_text,
        "chunk_count": None,
        "embedding_done": False,
        "error": None
    }

    result = chunk_and_embed_node(initial_state, db)

    if result.get("error"):
        logger.error(f"Resume pipeline failed for candidate {candidate_id}: {result['error']}")
    else:
        logger.info(f"Resume pipeline complete — {result.get('chunk_count')} chunks stored")

    return result