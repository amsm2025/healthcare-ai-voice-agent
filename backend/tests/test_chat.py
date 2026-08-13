from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_scheduling_intent():
    response = client.post("/api/v1/chat", json={"message": "I want to schedule an appointment"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "schedule_appointment"
    assert body["safe_to_continue"] is True


def test_emergency_guardrail():
    response = client.post("/api/v1/chat", json={"message": "I have severe chest pain"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "emergency"
    assert body["safe_to_continue"] is False
