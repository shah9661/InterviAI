import logging
from typing import List

from backend.app.core.logging import get_logger
from backend.app.ml.embeddings.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger("chunker", log_file="logs/chunker.log", level=logging.INFO)


def chunk_text(text: str) -> List[str]:
    if not text or not text.strip():
        logger.warning("Empty text passed to chunker")
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP   

    return chunks