import logging
import httpx
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def transcribe(self, content: bytes, filename: str, content_type: str) -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError("Voice transcription requires OPENAI_API_KEY in the .env file.")
        try:
            async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.openai_base_url.rstrip('/')}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    data={"model": self.settings.openai_transcription_model},
                    files={"file": (filename, content, content_type)},
                )
                response.raise_for_status()
            text = response.json().get("text", "").strip()
            if not text:
                raise RuntimeError("No speech was detected. Please try again.")
            return text
        except httpx.HTTPError as exc:
            logger.warning("Transcription provider request failed: %s", exc)
            raise RuntimeError("Voice transcription is temporarily unavailable.") from exc
