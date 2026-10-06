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

Build and run with Docker Compose:

```bash
docker compose up --build
```

App is exposed at <http://localhost:8000>.

## CI

GitHub Actions workflow at .github/workflows/ci.yml runs:

1. Python 3.12 setup
2. dependency install from requirements.txt
3. pytest -q

## Notes

This project is intentionally educational. It demonstrates auditable flows and integrity checks, not production-grade DRM or decentralized trust.
