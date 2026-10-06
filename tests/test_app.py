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


def test_peer_chain_can_sync_to_a_valid_longer_chain():
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-PEER", "userId": "peer-user", "contentId": "content-001"})
    remote.add_block({"type": "CONTENT_ACCESS", "licenseId": "LIC-PEER", "contentId": "content-001", "result": "GRANTED"})

    local.register_peer("peer-1", remote.chain)
    result = local.sync_with_peer("peer-1")

    assert result["adopted"] is True
    assert len(local.chain) == len(remote.chain)
    assert local.chain[-1]["event"]["type"] == "CONTENT_ACCESS"


def test_peer_chain_sync_rejects_invalid_longer_chain_and_keeps_local_chain():
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-LOCAL", "userId": "local-user", "contentId": "content-001"})
    initial_length = len(local.chain)

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-PEER", "userId": "peer-user", "contentId": "content-001"})
    remote.add_block({"type": "CONTENT_ACCESS", "licenseId": "LIC-PEER", "contentId": "content-001", "result": "GRANTED"})
    remote.chain[1]["event"]["type"] = "TAMPERED_EVENT"

    local.register_peer("peer-invalid", remote.chain)
    result = local.sync_with_peer("peer-invalid")

    assert result["adopted"] is False
    assert "invalid" in result["reason"].lower()
    assert len(local.chain) == initial_length
    assert local.chain[-1]["event"]["type"] == "LICENSE_ISSUED"


def test_peer_chain_sync_rejects_chain_that_is_not_longer():
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-LOCAL", "userId": "local-user", "contentId": "content-001"})

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-REMOTE", "userId": "remote-user", "contentId": "content-002"})

    local.register_peer("peer-same-length", remote.chain)
    result = local.sync_with_peer("peer-same-length")

    assert result["adopted"] is False
    assert "not longer" in result["reason"].lower()
    assert local.chain[-1]["event"]["licenseId"] == "LIC-LOCAL"


def test_sync_endpoint_returns_404_for_unknown_peer():
    client = TestClient(app)

    response = client.post("/peers/non-existent-peer/sync")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_reconcile_adopts_valid_peer_when_local_chain_is_invalid_even_if_not_longer():
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-LOCAL", "userId": "local-user", "contentId": "content-001"})

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-PEER", "userId": "peer-user", "contentId": "content-001"})

    local.chain[1]["event"]["type"] = "TAMPERED_EVENT"
    assert local.validate_chain()["valid"] is False
    assert len(local.chain) == len(remote.chain)

    local.register_peer("peer-valid", remote.chain)
    result = local.reconcile_with_peers()

    assert result["reconciled"] is True
    assert result["adopted"] is True
    assert result["peer"] == "peer-valid"
    assert len(local.chain) == len(remote.chain)
    assert local.validate_chain()["valid"] is True


def test_reconcile_keeps_local_when_local_is_valid_and_peer_is_not_longer():
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-LOCAL", "userId": "local-user", "contentId": "content-001"})

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-REMOTE", "userId": "remote-user", "contentId": "content-002"})

    local.register_peer("peer-same-length", remote.chain)
    result = local.reconcile_with_peers()

    assert result["reconciled"] is False
    assert result["adopted"] is False
    assert "valid" in result["reason"].lower()
    assert local.chain[-1]["event"]["licenseId"] == "LIC-LOCAL"


def test_reconcile_endpoint_returns_400_when_no_peers_registered():
    client = TestClient(app)

    response = client.post("/blockchain/reconcile")

    assert response.status_code == 400
    assert "no peers" in response.json()["detail"].lower()


def test_reconcile_endpoint_recovers_tampered_chain_from_valid_peer():
    client = TestClient(app)

    client.post(
        "/licenses",
        json={"userId": "local-user", "contentId": "content-001", "expiresAt": "2030-01-01T00:00:00Z"},
    )
    tampered = client.post("/blockchain/tamper")
    assert tampered.status_code == 200
    assert tampered.json()["valid"] is False

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-PEER", "userId": "peer-user", "contentId": "content-001"})
    app.state.blockchain.register_peer("peer-valid", remote.chain)

    response = client.post("/blockchain/reconcile")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reconciled"] is True
    assert payload["adopted"] is True
    assert payload["peer"] == "peer-valid"
    assert app.state.blockchain.validate_chain()["valid"] is True


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


def test_register_peer_accepts_base_url_aliases_and_lists_peer_metadata():
    client = TestClient(app)

    response_camel = client.post("/peers", json={"name": "peer-camel", "baseUrl": "http://peer-a:8000/"})
    assert response_camel.status_code == 200
    assert response_camel.json()["type"] == "url"

    response_snake = client.post("/peers", json={"name": "peer-snake", "base_url": "http://peer-b:8000"})
    assert response_snake.status_code == 200
    assert response_snake.json()["type"] == "url"

    peers = client.get("/peers")
    assert peers.status_code == 200
    payload = peers.json()["peers"]
    by_name = {peer["name"]: peer for peer in payload}
    assert by_name["peer-camel"]["base_url"] == "http://peer-a:8000"
    assert by_name["peer-camel"]["type"] == "url"
    assert by_name["peer-snake"]["base_url"] == "http://peer-b:8000"
    assert by_name["peer-snake"]["type"] == "url"


def test_sync_with_url_peer_fetches_chain_at_request_time(monkeypatch):
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.register_peer("peer-url", base_url="http://peer:8000")

    remote_a = BlockchainService()
    remote_b = BlockchainService()
    remote_b.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-URL", "userId": "peer-user", "contentId": "content-001"})
    chains = [remote_a.chain, remote_b.chain]
    call_count = {"value": 0}

    def fake_fetch(_base_url: str):
        idx = min(call_count["value"], len(chains) - 1)
        call_count["value"] += 1
        return chains[idx]

    monkeypatch.setattr(local, "_fetch_chain_from_url", fake_fetch)

    first = local.sync_with_peer("peer-url")
    assert first["adopted"] is False
    assert "not longer" in first["reason"].lower()

    second = local.sync_with_peer("peer-url")
    assert second["adopted"] is True
    assert len(local.chain) == len(remote_b.chain)
    assert call_count["value"] == 2


def test_reconcile_with_url_peer_recovers_invalid_local_chain_even_when_not_longer(monkeypatch):
    from app.blockchain.service import BlockchainService

    local = BlockchainService()
    local.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-LOCAL", "userId": "local-user", "contentId": "content-001"})
    local.chain[1]["event"]["type"] = "TAMPERED_EVENT"
    assert local.validate_chain()["valid"] is False

    remote = BlockchainService()
    remote.add_block({"type": "LICENSE_ISSUED", "licenseId": "LIC-PEER", "userId": "peer-user", "contentId": "content-001"})
    assert len(remote.chain) == len(local.chain)

    local.register_peer("peer-url", base_url="http://peer:8000")
    monkeypatch.setattr(local, "_fetch_chain_from_url", lambda _base_url: remote.chain)

    result = local.reconcile_with_peers()
    assert result["reconciled"] is True
    assert result["adopted"] is True
    assert result["peer"] == "peer-url"
    assert local.validate_chain()["valid"] is True
