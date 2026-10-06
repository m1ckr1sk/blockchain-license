# Project Brief: FastAPI DRM Blockchain Demonstrator

## Purpose

This project is a proof-of-concept for using a lightweight blockchain ledger to manage digital rights for protected API content. The goal is to demonstrate how license creation, validation, revocation, access auditing, and tamper detection can be modeled in a small backend service without attempting to build a production DRM platform.

## Problem Statement

Traditional content protection often relies on ad hoc authorization checks in application code. This project explores a more auditable model in which license events and access activity are recorded in a blockchain-like ledger so that behavior can be checked, historically reviewed, and tamper-detected.

## Goals

- Build a FastAPI application that exposes protected content endpoints
- Demonstrate blockchain-style event chaining with SHA256 integrity checks
- Support license issuance, validation, and revocation
- Track access attempts and successful content retrievals
- Show how a tampered chain can be detected by validation logic
- Demonstrate distributed ledger basics via peer registration and sync
- Support reconciliation from valid peers after local tampering
- Keep the implementation educational, minimal, and maintainable

## Non-Goals

- Real public blockchain deployment
- Production-grade DRM enforcement
- Copy-protection of downloaded media at the client device layer
- Advanced cryptographic key management or decentralized trust infrastructure
- Full multi-user identity, billing, or enterprise governance systems

## Target Users

- Developers learning FastAPI + blockchain concepts
- Technical stakeholders evaluating a simple DRM pattern
- Students and teams building educational prototypes

## Functional Scope

### Core Features

1. Genesis block creation on startup
2. Append new blocks with event payloads
3. Validate the integrity of the chain
4. Create and store licenses with expiry metadata
5. Revoke licenses and deny future access
6. Protect content access behind license validation
7. Record access events and audit activity
8. Expose endpoints for viewing chain state and validation status
9. Register peers and sync from longer valid peer chains
10. Reconcile local state from valid peers when tampering is detected

### API Surface

- `POST /licenses` to create a license
- `POST /licenses/{id}/revoke` to revoke a license
- `GET /content/{content_id}` to retrieve protected content when authorized
- `GET /health` for service health checks
- `GET /blockchain/validate` to verify chain integrity
- `GET /blockchain` to inspect stored blocks
- `POST /blockchain/tamper` to simulate tampering in a demo environment
- `POST /blockchain/reconcile` to recover local chain from valid peers
- `GET /peers` to inspect registered peers
- `POST /peers` to register a peer by name, with optional `baseUrl`/`base_url` for URL-based sync
- `POST /peers/{peer_name}/sync` to adopt a valid longer peer chain

## Proposed Technical Architecture

- Backend: Python 3.12 + FastAPI
- Schema validation: Pydantic
- Hashing: SHA256 (`hashlib`)
- Persistence: in-memory or file-backed storage for the demonstrator
- Testing: pytest
- Runtime: Uvicorn

## Ordered Delivery Stories

### Story 1: Project Foundation

- Create the application skeleton
- Define project layout and dependency setup
- Add a baseline README and contributor guidance

Acceptance criteria:

- The repository has a clean Python project structure
- Dependencies are documented
- Contributors know how to run the project locally

### Story 2: Blockchain Ledger

- Implement genesis block creation
- Add block creation logic
- Calculate and validate hashes
- Expose chain validation endpoints

Acceptance criteria:

- Chain starts with a valid genesis block
- Each block links to the previous hash
- Validation detects tampering

### Story 3: License Management

- Model license records and statuses
- Issue and revoke licenses
- Support expiry checks
- Add audit-friendly event creation

Acceptance criteria:

- License issuance produces a blockchain event
- Revoked licenses fail validation
- Expired licenses are rejected

### Story 4: Protected Content API

- Add content endpoints behind authorization checks
- Validate license presence, status, and expiry
- Record successful and failed access attempts

Acceptance criteria:

- Unauthorized requests are rejected with an appropriate HTTP status
- Authorized users receive content
- Access records are written to the ledger or audit trail

### Story 5: Demonstration and Testing

- Add tests for blockchain integrity and license enforcement
- Validate tamper detection behavior
- Confirm happy-path and denial flows

Acceptance criteria:

- Core behaviors are covered by automated tests
- Validation failures are easy to demonstrate in a dev environment

## Dependencies

- Python environment and package installation workflow
- FastAPI and Pydantic versions compatible with Python 3.12
- pytest for verification
- Basic repo-level conventions for linting and PR hygiene

## Handoffs to Specialist Agents

- Designer: define the user-facing dashboard and application flow for demonstration and audit reporting
- Backend Developer: implement the FastAPI routes, models, blockchain logic, and validation rules
- Frontend Developer: build a lightweight UI for viewing license state, chain validation, and content access results
- Test Engineer: add regression coverage for permission, expiry, and tamper scenarios

## Risks and Questions

- Should the prototype use in-memory storage or a file-backed persistence layer for demonstration simplicity?
- How much of the blockchain behavior should be exposed in the API versus kept internal to the service?
- Will the project need a minimal UI for the demo, or is an API-first model sufficient?
- Should the implementation prioritize strict educational clarity over realistic production-like behavior?

## Success Criteria

The project is successful when it clearly demonstrates:

- a blockchain-style ledger in code,
- secure-enough license validation for a demo environment,
- deterministic tamper detection,
- a working API workflow for license issuance and content access,
- and contributor-friendly developer standards.
