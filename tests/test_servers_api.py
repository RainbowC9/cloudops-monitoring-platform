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
def configure_test_environment():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    role_state["name"] = "Admin"

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    yield

    app.dependency_overrides.clear()

def valid_server_payload(
    *,
    name: str = "TEST-WEB-01",
    hostname: str = "test-web-01.demo.local",
    ip_address: str = "192.0.2.10",
):
    return {
        "name": name,
        "hostname": hostname,
        "ip_address": ip_address,
        "environment": "development",
        "operating_system": "Ubuntu Linux",
        "status": "online",
    }

def test_admin_can_create_server():
    response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "TEST-WEB-01"
    assert body["is_active"] is True

def test_viewer_cannot_create_server():
    role_state["name"] = "Viewer"

    response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    assert response.status_code == 403

def test_engineer_can_create_server():
    role_state["name"] = "Engineer"

    response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    assert response.status_code == 201

def test_invalid_ip_address_is_rejected():
    response = client.post(
        "/api/servers",
        json=valid_server_payload(
            ip_address="999.999.999.999"
        ),
    )

    assert response.status_code == 422

def test_duplicate_hostname_returns_conflict():
    first_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/servers",
        json=valid_server_payload(
            name="TEST-WEB-02",
        ),
    )

    assert second_response.status_code == 409

def test_viewer_can_list_servers():
    create_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    assert create_response.status_code == 201

    role_state["name"] = "Viewer"

    response = client.get(
        "/api/servers"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1

def test_server_environment_filter():
    client.post(
        "/api/servers",
        json=valid_server_payload(
            name="PROD-01",
            hostname="prod-01.demo.local",
            ip_address="192.0.2.20",
        )
        | {
            "environment": "production",
        },
    )

    client.post(
        "/api/servers",
        json=valid_server_payload(
            name="STAGING-01",
            hostname="staging-01.demo.local",
            ip_address="192.0.2.30",
        )
        | {
            "environment": "staging",
        },
    )

    response = client.get(
        "/api/servers",
        params={
            "environment": "production",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert (
        body["items"][0]["environment"]
        == "production"
    )

def test_engineer_can_update_server():
    create_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    server_id = create_response.json()["id"]

    role_state["name"] = "Engineer"

    update_response = client.put(
        f"/api/servers/{server_id}",
        json={
            "status": "maintenance",
        },
    )

    assert update_response.status_code == 200

    assert (
        update_response.json()["status"]
        == "maintenance"
    )

def test_engineer_cannot_deactivate_server():
    create_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    server_id = create_response.json()["id"]

    role_state["name"] = "Engineer"

    response = client.patch(
        f"/api/servers/{server_id}/deactivate"
    )

    assert response.status_code == 403

def test_admin_can_deactivate_server():
    create_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    server_id = create_response.json()["id"]

    response = client.patch(
        f"/api/servers/{server_id}/deactivate"
    )

    assert response.status_code == 200

    assert (
        response.json()["is_active"]
        is False
    )

def test_inactive_server_hidden_by_default():
    create_response = client.post(
        "/api/servers",
        json=valid_server_payload(),
    )

    server_id = create_response.json()["id"]

    client.patch(
        f"/api/servers/{server_id}/deactivate"
    )

    response = client.get(
        "/api/servers"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0

    response_with_inactive = client.get(
        "/api/servers",
        params={
            "include_inactive": True,
        },
    )

    assert (
        response_with_inactive.status_code
        == 200
    )

    assert (
        response_with_inactive.json()["total"]
        == 1
    )

def test_server_summary():
    client.post(
        "/api/servers",
        json=valid_server_payload(
            name="PROD-WEB-01",
            hostname="prod-web-01.demo.local",
            ip_address="192.0.2.40",
        )
        | {
            "environment": "production",
            "status": "online",
        },
    )

    client.post(
        "/api/servers",
        json=valid_server_payload(
            name="STAGING-01",
            hostname="staging-01.demo.local",
            ip_address="192.0.2.50",
        )
        | {
            "environment": "staging",
            "status": "warning",
        },
    )

    response = client.get(
        "/api/servers/summary"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert body["active"] == 2
    assert body["inactive"] == 0
    assert body["by_status"]["online"] == 1
    assert body["by_status"]["warning"] == 1
    assert (
        body["by_environment"]["production"]
        == 1
    )

    assert (
        body["by_environment"]["staging"]
        == 1
    )