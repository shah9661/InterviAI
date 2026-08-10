import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.db.models.resume  import ResumeChunk
from backend.app.ml.rag.chunker import chunk_text
from backend.app.ml.embeddings.embedder import get_embedding
from backend.app.core.logging import get_logger

logger = get_logger("context_builder", log_file="logs/context_builder.log", level=logging.INFO)


def store_resume_vector(db: Session, candidate_id: int, resume_text: str) -> int:
    try:
        db.query(ResumeChunk).filter(ResumeChunk.candidate_id == candidate_id).delete()
        db.commit()

        chunks = chunk_text(resume_text)
        logger.info(f"Chunk count for candidate {candidate_id}: {len(chunks)}")

        if not chunks:
            logger.warning(f"No chunks generated for candidate {candidate_id}")
            return 0

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            resume_chunk = ResumeChunk(
                candidate_id=candidate_id,
                chunk_index=i,
                chunk_text=chunk,
                embedding=embedding
            )
            db.add(resume_chunk)

        db.commit()
        logger.info(f"Stored {len(chunks)} chunks for candidate {candidate_id}")
        return len(chunks)

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error storing resume vectors for candidate {candidate_id}: {e}")
        raise


def get_full_resume_context(db: Session, candidate_id: int) -> str:
    try:
        chunks = (
            db.query(ResumeChunk)
            .filter(ResumeChunk.candidate_id == candidate_id)
            .order_by(ResumeChunk.chunk_index)
            .all()
        )
        return "\n".join([c.chunk_text for c in chunks])
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching resume context for candidate {candidate_id}: {e}")
        raise