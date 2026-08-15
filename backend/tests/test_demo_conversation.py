from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def ask(message: str) -> dict:
    response = client.post("/api/v1/chat", json={"message": message})
    assert response.status_code == 200
    return response.json()

def test_greeting_has_distinct_response():
    assert ask("Hola!")["intent"] == "greeting"

def test_preferred_schedule_advances_flow():
    result = ask("I want a Monday 9 AM schedule")
    assert result["intent"] == "appointment_time"
    assert "name and email" in result["reply"]

def test_contact_details_completes_demo_request():
    result = ask("Martin, martin@example.com")
    assert result["intent"] == "contact_details"
    assert "captured" in result["reply"]
