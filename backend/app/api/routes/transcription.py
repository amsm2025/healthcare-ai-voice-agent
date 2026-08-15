from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.transcription_service import TranscriptionService

router = APIRouter(prefix="/api/v1", tags=["voice"])
service = TranscriptionService()
MAX_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg"}

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict[str, str]:
    content_type = (file.content_type or "").split(";")[0]
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio format.")
    content = await file.read(MAX_AUDIO_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The audio recording is empty.")
    if len(content) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="The audio recording is too large.")
    try:
        return {"text": await service.transcribe(content, file.filename or "voice.webm", content_type)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
