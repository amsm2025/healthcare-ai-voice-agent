from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.routes import bookings as bookings_route
from app.api.routes import chat as chat_route
from app.main import app

client = TestClient(app)


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeAsyncClient:
    """Minimal httpx.AsyncClient replacement for provider integration tests."""

    response_payload: dict = {}
    last_url: str | None = None
    last_headers: dict | None = None
    last_json: dict | None = None

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, *, headers: dict, json: dict):
        type(self).last_url = url
        type(self).last_headers = headers
        type(self).last_json = json
        return FakeResponse(type(self).response_payload)


def test_live_llm_provider_path(monkeypatch):
    settings = SimpleNamespace(
        llm_mode="live",
        openai_api_key="test-openai-key",
        openai_model="test-model",
        openai_base_url="https://api.openai.test/v1",
        openai_timeout_seconds=5.0,
    )

    monkeypatch.setattr(chat_route.service, "settings", settings)

    from app.services import llm_service

    FakeAsyncClient.response_payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": "I can help you arrange that appointment.",
                    }
                ],
            }
        ]
    }

    monkeypatch.setattr(llm_service.httpx, "AsyncClient", FakeAsyncClient)

    response = client.post(
        "/api/v1/chat",
        json={"message": "Please schedule an appointment for me."},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["reply"] == "I can help you arrange that appointment."
    assert body["intent"] == "schedule_appointment"
    assert body["safe_to_continue"] is True

    assert FakeAsyncClient.last_url == "https://api.openai.test/v1/responses"
    assert FakeAsyncClient.last_headers["Authorization"] == "Bearer test-openai-key"
    assert FakeAsyncClient.last_json["model"] == "test-model"
    assert FakeAsyncClient.last_json["store"] is False


def test_live_calcom_provider_path(monkeypatch):
    settings = SimpleNamespace(
        calcom_mode="live",
        calcom_api_key="test-calcom-key",
        calcom_event_type_id="12345",
        calcom_base_url="https://api.cal.test",
        calcom_api_version="2026-02-25",
        calcom_timeout_seconds=5.0,
    )

    monkeypatch.setattr(bookings_route.service, "settings", settings)

    from app.services import calcom_service

    FakeAsyncClient.response_payload = {
        "data": {
            "uid": "booking-abc123",
            "status": "accepted",
            "start": "2026-09-01T01:00:00Z",
        }
    }

    monkeypatch.setattr(calcom_service.httpx, "AsyncClient", FakeAsyncClient)

    response = client.post(
        "/api/v1/bookings",
        json={
            "name": "Demo Patient",
            "email": "demo@example.com",
            "start_time": "2026-09-01T09:00:00+08:00",
            "reason": "General consultation",
            "timezone": "Asia/Manila",
            "language": "en",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["booking_id"] == "booking-abc123"
    assert body["status"] == "accepted"

    assert FakeAsyncClient.last_url == "https://api.cal.test/v2/bookings"
    assert FakeAsyncClient.last_headers["Authorization"] == "Bearer test-calcom-key"
    assert FakeAsyncClient.last_headers["cal-api-version"] == "2026-02-25"
    assert FakeAsyncClient.last_json["eventTypeId"] == 12345
    assert FakeAsyncClient.last_json["attendee"]["timeZone"] == "Asia/Manila"
    assert FakeAsyncClient.last_json["start"] == "2026-09-01T01:00:00Z"


def test_live_calcom_missing_credentials_returns_502(monkeypatch):
    settings = SimpleNamespace(
        calcom_mode="live",
        calcom_api_key="",
        calcom_event_type_id="12345",
    )

    monkeypatch.setattr(bookings_route.service, "settings", settings)

    response = client.post(
        "/api/v1/bookings",
        json={
            "name": "Demo Patient",
            "email": "demo@example.com",
            "start_time": "2026-09-01T09:00:00Z",
            "timezone": "UTC",
            "language": "en",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Cal.com live mode requires CALCOM_API_KEY."
