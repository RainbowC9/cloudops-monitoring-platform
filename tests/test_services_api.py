from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.models  # noqa: F401
from app.database import Base, get_db
from app.dependencies import get_current_user
from app.main import app
from app.models.server import Server


test_engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)

role_state = {
    "name": "Admin",
}

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return SimpleNamespace(
        id=999,
        username="test-user",
        email="test@example.test",
        is_active=True,
        role=SimpleNamespace(
            name=role_state["name"],
        ),
    )

client = TestClient(app)

@pytest.fixture(autouse=True)
def test_environment():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    role_state["name"] = "Admin"

    with TestingSessionLocal() as db:
        server = Server(
            name="TEST-SERVER-01",
            hostname="test-server-01.local",
            ip_address="127.0.0.1",
            environment="development",
            operating_system="Test OS",
            status="online",
            is_active=True,
        )

        db.add(server)
        db.commit()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    yield

    app.dependency_overrides.clear()

def http_payload():
    return {
        "server_id": 1,
        "name": "Test HTTP",
        "service_type": "http",
        "endpoint": (
            "http://127.0.0.1:8001/health"
        ),
    }

def tcp_payload():
    return {
        "server_id": 1,
        "name": "Test TCP",
        "service_type": "tcp",
        "endpoint": "127.0.0.1",
        "port": 8001,
    }

def test_admin_can_create_http_service():
    response = client.post(
        "/api/services",
        json=http_payload(),
    )
    assert response.status_code == 201
    assert (
        response.json()["service_type"]
        == "http"
    )

def test_engineer_can_create_service():
    role_state["name"] = "Engineer"

    response = client.post(
        "/api/services",
        json=tcp_payload(),
    )

    assert response.status_code == 201

def test_viewer_cannot_create_service():
    role_state["name"] = "Viewer"

    response = client.post(
        "/api/services",
        json=http_payload(),
    )

    assert response.status_code == 403

def test_tcp_service_requires_port():
    payload = tcp_payload()
    del payload["port"]
    response = client.post(
        "/api/services",
        json=payload,
    )
    assert response.status_code == 422

def test_invalid_http_scheme_rejected():
    payload = http_payload()

    payload["endpoint"] = (
        "ftp://127.0.0.1/test"
    )

    response = client.post(
        "/api/services",
        json=payload,
    )
    assert response.status_code == 422

def test_duplicate_service_rejected():
    first = client.post(
        "/api/services",
        json=http_payload(),
    )
    assert first.status_code == 201
    second = client.post(
        "/api/services",
        json=http_payload(),
    )

    assert second.status_code == 409

def test_viewer_can_list_services():
    client.post(
        "/api/services",
        json=http_payload(),
    )

    role_state["name"] = "Viewer"

    response = client.get(
        "/api/services"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

def test_admin_can_deactivate_service():
    created = client.post(
        "/api/services",
        json=http_payload(),
    )

    service_id = (
        created.json()["id"]
    )

    response = client.patch(
        f"/api/services/{service_id}/deactivate"
    )
    assert response.status_code == 200
    assert (
        response.json()["is_active"]
        is False
    )

def test_engineer_cannot_deactivate_service():
    created = client.post(
        "/api/services",
        json=http_payload(),
    )

    service_id = (
        created.json()["id"]
    )

    role_state["name"] = "Engineer"

    response = client.patch(
        f"/api/services/{service_id}/deactivate"
    )

    assert response.status_code == 403