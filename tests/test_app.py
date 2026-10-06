from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.blockchain.service import BlockchainService
from app.drm.service import DRMService
from app.main import app


@pytest.fixture(autouse=True)
def reset_app_state():
    app.state.blockchain = BlockchainService()
    app.state.drm_service = DRMService(app.state.blockchain)
    yield
    app.state.blockchain = BlockchainService()
    app.state.drm_service = DRMService(app.state.blockchain)


def test_genesis_block_is_created_and_chain_is_valid():
    client = TestClient(app)

    response = client.get("/blockchain/validate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["block_count"] == 1
    assert payload["blocks"][0]["index"] == 0
    assert payload["blocks"][0]["previous_hash"] == ""


def test_license_creation_records_event_and_is_accessible():
    client = TestClient(app)
    expiry = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = client.post(
        "/licenses",
        json={"userId": "alice", "contentId": "content-001", "expiresAt": expiry},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "ACTIVE"
    assert payload["userId"] == "alice"
    assert payload["contentId"] == "content-001"
    assert payload["licenseId"].startswith("LIC-")

    content_response = client.get("/content/content-001", params={"licenseId": payload["licenseId"]})
    assert content_response.status_code == 200
    assert content_response.json()["contentId"] == "content-001"


def test_revoked_and_expired_licenses_are_rejected():
    client = TestClient(app)
    soon_expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    created = client.post(
        "/licenses",
        json={"userId": "bob", "contentId": "content-002", "expiresAt": soon_expiry},
    )
    license_id = created.json()["licenseId"]

    revoke_response = client.post(f"/licenses/{license_id}/revoke")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["status"] == "REVOKED"

    denied = client.get("/content/content-002", params={"licenseId": license_id})
    assert denied.status_code == 403

    expired = client.post(
        "/licenses",
        json={"userId": "carol", "contentId": "content-003", "expiresAt": "2020-01-01T00:00:00Z"},
    )
    expired_license_id = expired.json()["licenseId"]

    expired_response = client.get("/content/content-003", params={"licenseId": expired_license_id})
    assert expired_response.status_code == 403


def test_chain_tampering_is_detected():
    client = TestClient(app)
    response = client.get("/blockchain")
    assert response.status_code == 200

    blocks = response.json()["blocks"]
    if len(blocks) > 1:
        client.post("/licenses", json={"userId": "dave", "contentId": "content-004", "expiresAt": "2030-01-01T00:00:00Z"})

    tampered = client.get("/blockchain/validate")
    assert tampered.status_code == 200
    assert tampered.json()["valid"] is True

    # Direct mutation should be caught by the underlying validation logic.
    blockchain_state = app.state.blockchain
    if len(blockchain_state.chain) > 1:
        blockchain_state.chain[1]["event"]["type"] = "TAMPERED_EVENT"
        assert blockchain_state.validate_chain()["valid"] is False


def test_missing_license_is_rejected():
    client = TestClient(app)

    response = client.get("/content/content-999", params={"licenseId": "LIC-DOES-NOT-EXIST"})

    assert response.status_code == 403


def test_demo_content_id_is_supported_by_the_license_flow():
    client = TestClient(app)
    expiry = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = client.post(
        "/licenses",
        json={"userId": "frank", "contentId": "course-module-01", "expiresAt": expiry},
    )

    assert response.status_code == 201
    license_id = response.json()["licenseId"]

    content_response = client.get("/content/course-module-01", params={"licenseId": license_id})
    assert content_response.status_code == 200
    assert content_response.json()["contentId"] == "course-module-01"


def test_content_id_mismatch_is_rejected():
    client = TestClient(app)
    expiry = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    created = client.post(
        "/licenses",
        json={"userId": "mis-match-user", "contentId": "content-001", "expiresAt": expiry},
    )
    assert created.status_code == 201
    license_id = created.json()["licenseId"]

    response = client.get("/content/content-002", params={"licenseId": license_id})
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: CONTENT_MISMATCH"


def test_content_access_is_denied_when_blockchain_is_tampered():
    client = TestClient(app)
    expiry = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    created = client.post(
        "/licenses",
        json={"userId": "erin", "contentId": "content-004", "expiresAt": expiry},
    )
    assert created.status_code == 201
    license_id = created.json()["licenseId"]

    tampered = client.post("/blockchain/tamper")
    assert tampered.status_code == 200
    assert tampered.json()["valid"] is False

    denied = client.get("/content/content-004", params={"licenseId": license_id})
    assert denied.status_code == 403
    assert "BLOCKCHAIN" in denied.json()["detail"]


def test_health_endpoint_and_tamper_endpoint_work_as_expected():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    create = client.post(
        "/licenses",
        json={"userId": "erin", "contentId": "content-004", "expiresAt": "2030-01-01T00:00:00Z"},
    )
    assert create.status_code == 201

    tamper = client.post("/blockchain/tamper")
    assert tamper.status_code == 200
    assert tamper.json()["valid"] is False

    validation = client.get("/blockchain/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is False
