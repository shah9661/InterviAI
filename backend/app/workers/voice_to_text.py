from backend.app.ml.llm.client import get_voice_llm
from backend.app.core.logging import get_logger
import logging

logger = get_logger("voice_worker", log_file="logs/voice_worker.log", level=logging.INFO)

client=get_voice_llm()
async def transcribe_audio(filename: str, audio_bytes: bytes) -> str:
    try:
        transcription=client.audio.transcriptions.create(
            file=(filename,audio_bytes),
            model="whisper-large-v3-turbo"
        )
        text=transcription.text
        return text
    except Exception as e:
        logger.error(f"Unable to transcripts {e}")
        raise