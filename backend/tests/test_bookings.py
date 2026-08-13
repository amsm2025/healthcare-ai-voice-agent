from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_demo_booking():
    response = client.post(
        "/api/v1/bookings",
        json={
            "name": "Demo Patient",
            "email": "demo@example.com",
            "start_time": "2026-09-01T09:00:00Z",
            "reason": "General consultation",
            "timezone": "Asia/Manila",
            "language": "en",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["booking_id"].startswith("demo-")
    assert body["status"] == "confirmed-demo"
