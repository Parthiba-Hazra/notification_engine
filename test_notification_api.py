from fastapi.testclient import TestClient
from notification_service import app

client = TestClient(app)

def test_send_notification():
    response = client.post("/send-notification/", json={
        "channel": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "message": "This is a test message"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
