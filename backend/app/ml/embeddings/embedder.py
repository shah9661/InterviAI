import logging
from typing import List
from sentence_transformers import SentenceTransformer

from backend.app.core.logging import get_logger
from backend.app.ml.embeddings.config import EMBEDDING_MODEL_NAME

logger = get_logger("embedder", log_file="logs/embedder.log", level=logging.INFO)

try:
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info(f"Embedding model loaded: {EMBEDDING_MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise


def get_embedding(text: str) -> List[float]:
    try:
        text = text.replace("\n", " ")
        return model.encode(text).tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise