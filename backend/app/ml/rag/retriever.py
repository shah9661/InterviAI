import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.logging import get_logger
from backend.app.ml.embeddings.embedder import get_embedding

logger = get_logger("retriever", log_file="logs/retriever.log", level=logging.INFO)


def search_similar_chunk(db: Session, candidate_id: int, query: str, top_k: int = 3) -> List[dict]:
    try:
        query_embedding = get_embedding(query)

        result = db.execute(
            sql_text("""
                SELECT
                    chunk_text,
                    chunk_index,
                    1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM resume_chunks
                WHERE candidate_id = :candidate_id
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {
                "embedding": str(query_embedding),
                "candidate_id": candidate_id,
                "top_k": top_k
            }
        ).fetchall()

        return [
            {
                "chunk_text": row.chunk_text,
                "chunk_index": row.chunk_index,
                "similarity": round(row.similarity, 4)
            }
            for row in result
        ]

    except SQLAlchemyError as e:
        logger.error(f"DB error searching resume chunks for candidate {candidate_id}: {e}")
        raise