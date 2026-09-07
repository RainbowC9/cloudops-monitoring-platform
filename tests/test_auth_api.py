from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_authenticated_endpoint_requires_token():
    response = client.get(
        "/api/auth/me"
    )

    assert response.status_code == 401


def test_health_endpoint_remains_public():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"