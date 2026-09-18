from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import (
    Base,
    get_db,
)
from app.dependencies import (
    get_current_user,
)
from app.main import app
from app.models.server import Server
from app.routers import (
    metrics as metrics_router,
)


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


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return SimpleNamespace(
        id=999,
        username="metrics-test-user",
        email="metrics@example.test",
        is_active=True,
        role=SimpleNamespace(
            name="Viewer",
        ),
    )


client = TestClient(
    app
)


@pytest.fixture(autouse=True)
def metrics_test_environment(
    monkeypatch,
):
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    with TestingSessionLocal() as db:
        server = Server(
            name="DEV-CLOUDOPS-01",
            hostname="localhost",
            ip_address="127.0.0.1",
            environment="development",
            operating_system="Windows Test Host",
            status="online",
            is_active=True,
        )

        db.add(
            server
        )

        db.commit()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    monkeypatch.setattr(
        metrics_router.prometheus_client,
        "health",
        lambda: True,
    )

    monkeypatch.setattr(
        metrics_router.prometheus_client,
        "cpu_percent",
        lambda instance: 25.5,
    )

    monkeypatch.setattr(
        metrics_router.prometheus_client,
        "memory_percent",
        lambda instance: 60.25,
    )

    monkeypatch.setattr(
        metrics_router.prometheus_client,
        "disk_usage",
        lambda instance: [
            {
                "volume": "C:",
                "used_percent": 72.75,
            }
        ],
    )

    yield

    app.dependency_overrides.clear()


def test_prometheus_health():
    response = client.get(
        "/api/metrics/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "healthy"
    )


def test_cpu_metrics():
    response = client.get(
        "/api/metrics/servers/1/cpu"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["value"] == 25.5
    assert body["unit"] == "percent"
    assert body["available"] is True


def test_memory_metrics():
    response = client.get(
        "/api/metrics/servers/1/memory"
    )

    assert response.status_code == 200

    assert (
        response.json()["value"]
        == 60.25
    )


def test_disk_metrics():
    response = client.get(
        "/api/metrics/servers/1/disk"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body["disks"]
    ) == 1

    assert (
        body["disks"][0]["volume"]
        == "C:"
    )

    assert (
        body["disks"][0]["used_percent"]
        == 72.75
    )


def test_metrics_overview():
    response = client.get(
        "/api/metrics/servers/1/overview"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["cpu_percent"] == 25.5

    assert (
        body["memory_percent"]
        == 60.25
    )

    assert len(
        body["disks"]
    ) == 1

def test_missing_server_returns_404():
    response = client.get(
        "/api/metrics/servers/999/cpu"
    )

    assert response.status_code == 404

def test_inactive_server_returns_409():
    with TestingSessionLocal() as db:
        server = db.get(
            Server,
            1,
        )

        server.is_active = False

        db.commit()

    response = client.get(
        "/api/metrics/servers/1/cpu"
    )

    assert response.status_code == 409