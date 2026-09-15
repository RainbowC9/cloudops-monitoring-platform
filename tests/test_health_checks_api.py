from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.models  # noqa: F401
from app.routers import (
    health_checks as health_checks_router,
)
from app.database import Base, get_db
from app.dependencies import get_current_user
from app.main import app
from app.models.server import Server
from app.models.service import Service
from app.services.health_checks import CheckResult


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
def test_environment(
    monkeypatch,
):
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    role_state["name"] = "Admin"

    with TestingSessionLocal() as db:
        server = Server(
            name="TEST-SERVER",
            hostname="test-server.local",
            ip_address="127.0.0.1",
            environment="development",
            operating_system="Test OS",
            status="online",
            is_active=True,
        )

        db.add(server)
        db.flush()

        service = Service(
            server_id=server.id,
            name="Test HTTP Service",
            service_type="http",
            endpoint=(
                "http://127.0.0.1:8001/health"
            ),
            port=None,
            status="unknown",
            is_active=True,
        )

        db.add(service)
        db.commit()

    def fake_run_service_check(
        service,
    ):
        return CheckResult(
            check_type="http",
            status="healthy",
            response_time_ms=12.5,
            details={
                "status_code": 200,
                "target": service.endpoint,
            },
        )

    monkeypatch.setattr(
        health_checks_router,
        "run_service_check",
        fake_run_service_check,
    )

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    yield

    app.dependency_overrides.clear()

def test_admin_can_run_health_check():
    response = client.post(
        "/api/health-checks/services/1/run"
    )

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "healthy"
    assert body["check_type"] == "http"

    assert (
        body["response_time_ms"]
        == 12.5
    )

def test_engineer_can_run_health_check():
    role_state["name"] = "Engineer"

    response = client.post(
        "/api/health-checks/services/1/run"
    )

    assert response.status_code == 201

def test_viewer_cannot_run_health_check():
    role_state["name"] = "Viewer"

    response = client.post(
        "/api/health-checks/services/1/run"
    )
    assert response.status_code == 403

def test_viewer_can_list_health_checks():
    client.post(
        "/api/health-checks/services/1/run"
    )

    role_state["name"] = "Viewer"

    response = client.get(
        "/api/health-checks"
    )
    assert response.status_code == 200
    assert (
        response.json()["total"]
        == 1
    )

def test_latest_health_check():
    client.post(
        "/api/health-checks/services/1/run"
    )

    response = client.get(
        "/api/health-checks/services/1/latest"
    )
    assert response.status_code == 200
    assert (
        response.json()["status"]
        == "healthy"
    )

def test_health_check_summary():
    client.post(
        "/api/health-checks/services/1/run"
    )

    response = client.get(
        "/api/health-checks/summary"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_checks"] == 1
    assert body["healthy_checks"] == 1
    assert body["unhealthy_checks"] == 0
    assert body["monitored_services"] == 1
    assert (
        body["by_type"]["http"]
        == 1
    )