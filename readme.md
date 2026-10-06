# FastAPI DRM Blockchain Demonstrator

[![CI](https://github.com/m1ckr1sk/blockchain-license/actions/workflows/ci.yml/badge.svg)](https://github.com/m1ckr1sk/blockchain-license/actions/workflows/ci.yml)

Educational proof of concept showing license-gated content access backed by a lightweight blockchain ledger, including tamper detection and peer-based reconciliation.

## Overview

The API stores license lifecycle and access events in a hash-linked chain. Before protected content is returned, the backend validates:

- chain integrity
- license existence
- content/license match
- license status and expiration

The demo now also includes distributed basics:

- peer registration
- peer sync with longest valid chain adoption
- reconciliation API to recover local state after tampering

## Current Architecture

```text
Browser UI (static files from FastAPI)
            |
            v
      FastAPI Routes
            |
   +--------+--------+
   |                 |
   v                 v
DRM Service     Blockchain Service
   |                 |
   +--------+--------+
            |
            v
 In-memory license store + blockchain event ledger
```

Key modules:

- API routes: license, blockchain, peer, content, health
- DRM service: issue/revoke/validate/record access
- Blockchain service: add block, validate chain, tamper simulation, peer sync, reconcile
- Frontend dashboard: operational demo of license and chain state

## API Endpoints

### Health

- GET /health

### License Management

- GET /licenses
- GET /licenses/{license_id}
- POST /licenses
- POST /licenses/{license_id}/revoke

### Protected Content

- GET /content/{content_id}?licenseId={license_id}

### Blockchain

- GET /blockchain
- GET /blockchain/validate
- POST /blockchain/tamper
- POST /blockchain/reconcile

### Peer Operations

- GET /peers
- POST /peers
- POST /peers/{peer_name}/sync

## Tamper and Recovery Workflow

1. Normal operation: issue license and access content, generating immutable events.
2. Tamper simulation: call POST /blockchain/tamper to intentionally mutate the latest block.
3. Validation failure: GET /blockchain/validate returns invalid and protected content access is denied.
4. Register peer metadata: POST /peers with a peer name.
5. Recover state: POST /blockchain/reconcile adopts the best valid peer chain when local chain is invalid (or when a longer valid peer chain is available).

## Frontend Capabilities

The root UI at / provides a single-page operational dashboard:

- create and revoke licenses
- request protected content and view grant/deny result
- validate chain and simulate tampering
- register/sync peers
- inspect ledger events
- view issued licenses in a table

The issued licenses table shows per-license details and a derived current state:

- ACTIVE
- REVOKED
- EXPIRED

## Local Setup

### Requirements

- Python 3.12
- pip

### Run Locally

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://localhost:8000> for the UI.

## Testing

Run automated tests:

```bash
pytest -q
```

The current test suite covers:

- license issuance/revocation/expiry checks
- content access authorization decisions
- tamper detection
- peer sync rules
- reconciliation recovery behavior

## Docker

Build and run two demo nodes with Docker Compose:

```bash
docker compose up --build
```

Compose demo endpoints:

- Node A UI/API: <http://localhost:8001>
- Node B UI/API: <http://localhost:8002>

Peer URL pattern between containers (for peer registration/sync):

- from node-a to node-b: `http://node-b:8000`
- from node-b to node-a: `http://node-a:8000`

Local non-Docker single-node development remains unchanged via `uvicorn app.main:app --reload` at <http://localhost:8000>.

### Two-Node Sync + Reconcile Demo (Windows PowerShell)

The following steps are copy/paste-ready for PowerShell and exercise peer sync, tamper detection, and reconciliation.

1. Start both nodes with one command:

```powershell
docker compose up --build -d
```

1. Register node-b as a peer of node-a using `baseUrl`:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/peers -ContentType 'application/json' -Body '{"name":"node-b","baseUrl":"http://node-b:8000"}'
```

1. Create extra activity on node-b (adds multiple blocks):

```powershell
$license = Invoke-RestMethod -Method Post -Uri http://localhost:8002/licenses -ContentType 'application/json' -Body '{"userId":"demo-user","contentId":"content-001","expiresAt":"2030-01-01T00:00:00Z"}'
Invoke-RestMethod -Method Get -Uri ("http://localhost:8002/content/content-001?licenseId=" + $license.licenseId)
Invoke-RestMethod -Method Get -Uri http://localhost:8002/blockchain/validate
```

1. Sync node-a from node-b and verify adoption:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/peers/node-b/sync
Invoke-RestMethod -Method Get -Uri http://localhost:8001/blockchain/validate
```

Expected in sync response: `"adopted": true`.

1. Tamper node-a and run reconcile:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/blockchain/tamper
Invoke-RestMethod -Method Get -Uri http://localhost:8001/blockchain/validate
Invoke-RestMethod -Method Post -Uri http://localhost:8001/blockchain/reconcile
```

1. Verify node-a chain is valid again:

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8001/blockchain/validate
```

Expected after reconcile: validation returns `"valid": true`.

Optional `curl.exe` equivalents:

```powershell
curl.exe -s -X POST http://localhost:8001/peers -H "Content-Type: application/json" -d "{\"name\":\"node-b\",\"baseUrl\":\"http://node-b:8000\"}"
curl.exe -s -X POST http://localhost:8001/peers/node-b/sync
curl.exe -s -X POST http://localhost:8001/blockchain/tamper
curl.exe -s -X POST http://localhost:8001/blockchain/reconcile
curl.exe -s http://localhost:8001/blockchain/validate
```

## CI

GitHub Actions workflow at .github/workflows/ci.yml runs:

1. Python 3.12 setup
2. dependency install from requirements.txt
3. pytest -q

## Notes

This project is intentionally educational. It demonstrates auditable flows and integrity checks, not production-grade DRM or decentralized trust.
