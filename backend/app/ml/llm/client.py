import logging
from langchain_openai import ChatOpenAI
from backend.app.core.logging import get_logger
from backend.app.core.config import settings
from groq import Groq

logger = get_logger("llm_client", log_file="logs/llm_client.log", level=logging.INFO)


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    try:
        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=temperature,
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        raise


def get_voice_llm():
    try:
        return Groq(api_key=settings.GROQ_API_KEY_VOICE)
    except Exception as e:
        logger.error(f"Failed to initialize voice LLM client: {e}")
        raise

