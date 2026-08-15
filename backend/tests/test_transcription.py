from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.api.routes import transcription as transcription_route
from app.main import app

client = TestClient(app)

def test_transcription_requires_key(monkeypatch):
    monkeypatch.setattr(transcription_route.service, "settings", SimpleNamespace(openai_api_key=""))
    response = client.post("/api/v1/transcribe", files={"file": ("voice.webm", b"demo-audio", "audio/webm")})
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]

def test_transcription_rejects_invalid_type():
    response = client.post("/api/v1/transcribe", files={"file": ("voice.txt", b"not-audio", "text/plain")})
    assert response.status_code == 415
