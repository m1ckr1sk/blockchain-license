# FastAPI DRM Blockchain Demonstrator

A simple proof-of-concept demonstrating how a blockchain-style ledger can be used for digital rights management (DRM) when protecting API-delivered content.

## Overview

This project shows how API access can be controlled by validating licenses stored on a lightweight blockchain.

The blockchain does not store the content itself. Instead, it records:

- License creation events
- License revocation events
- Content access events
- Download counts
- Ownership history

When a client requests protected content, the API validates the license against the blockchain before returning the resource.

## Objectives

Demonstrate:

- FastAPI application development
- REST API design
- Simple blockchain implementation
- DRM concepts
- License validation
- Access auditing
- Tamper detection
- System architecture

## Quick Local Demo UI

A lightweight browser demo is included to showcase the educational flow without requiring a live backend.

1. Open a terminal in the repository root.
2. Run `python -m http.server 8000`.
3. Visit `http://localhost:8000` in a browser.
4. Use the page to create a license, validate the ledger, request protected content, and simulate tampering.

This interface focuses on the core learning journey: license issuance, blockchain integrity checks, and protected content access decisions.

## Architecture

```text
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ FastAPI API  │
└──────┬───────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│ DRM Service  │      │ Blockchain   │
│              │      │ Ledger       │
└──────┬───────┘      └──────┬───────┘
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│ Content      │      │ Audit/Event  │
│ Repository   │      │ Records      │
└──────────────┘      └──────────────┘
```

## Features

- Blockchain ledger
- SHA256 hashing
- Immutable chain
- Chain validation
- Event recording
- DRM license creation and revocation
- Ownership verification
- Expiration support
- Download tracking
- Protected content API
- License checks
- Audit logging

## Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- SHA256 via `hashlib`
- pytest

## Project Structure

```text
app/
├── main.py
├── blockchain/
│   ├── block.py
│   ├── blockchain.py
│   └── validator.py
├── drm/
│   ├── models.py
│   ├── service.py
│   └── repository.py
├── api/
│   ├── licenses.py
│   ├── content.py
│   └── blockchain.py
├── storage/
│   └── content_store.py
└── tests/
```

## Data Model

### Block

```json
{
  "index": 1,
  "timestamp": "2026-01-01T12:00:00Z",
  "previous_hash": "...",
  "hash": "...",
  "event": {
    "type": "LICENSE_CREATED"
  }
}
```

### License

```json
{
  "licenseId": "LIC-001",
  "userId": "alice",
  "contentId": "content-001",
  "expiresAt": "2027-01-01T00:00:00Z",
  "status": "ACTIVE"
}
```

## Workflow

### Create License

`POST /licenses`

Creates a license and records a blockchain event.

### Access Content

`GET /content/content-001`

#### Validation steps

1. User provides a license identifier.
2. API locates the license.
3. API validates chain integrity.
4. API validates license status.
5. API checks expiration.
6. Access event is written.
7. Content is returned.

### Revoke License

`POST /licenses/{id}/revoke`

Creates a revocation event on the blockchain.

### Example access sequence

```text
Create License
      │
      ▼
Blockchain Event Added
      │
      ▼
Request Content
      │
      ▼
Validate Blockchain
      │
      ▼
Validate License
      │
      ▼
Record Access Event
      │
      ▼
Return Data
```

## Example API Calls

### Create License

```bash
curl -X POST \
  http://localhost:8000/licenses \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "alice",
    "contentId": "content-001",
    "expiresAt": "2027-01-01T00:00:00Z"
  }'
```

### Retrieve Content

```bash
curl "http://localhost:8000/content/content-001?licenseId=LIC-001"
```

### Validate Chain

```bash
curl http://localhost:8000/blockchain/validate
```

## Future Enhancements

- JWT authentication
- Digital signatures
- Public/private key ownership
- Encrypted content
- Smart contracts
- Distributed blockchain nodes
- Usage-based licensing
- Subscription licensing
- Additional disclaimers and policy controls

> This is an educational demonstrator and not a production DRM solution.
>
> Content retrieved by clients can still be copied, screenshotted, or redistributed.
>
> The purpose is to demonstrate immutable license tracking and auditability.

# User Stories

## Epic 1: Blockchain Ledger

### US-001: Create Genesis Block

As a system, I want a genesis block to be automatically created so that the blockchain starts from a known state.

#### Acceptance Criteria

- Genesis block exists on startup
- Index is zero
- Previous hash is empty
- Chain contains one block

### US-002: Add Block

As a DRM service, I want to append events to the chain so that all license activity is auditable.

#### Acceptance Criteria

- New block is hash linked
- Event payload is stored
- Timestamp is recorded
- Block hash is generated

### US-003: Validate Chain

As an administrator, I want to validate the blockchain so that tampering can be detected.

#### Acceptance Criteria

- API endpoint exists
- All hashes are verified
- Returns valid/invalid status

## Epic 2: License Management

### US-004: Create License

As a content publisher, I want to issue a license so that users can access content.

#### Acceptance Criteria

- License is generated
- Unique identifier is assigned
- Expiry date is supported
- Blockchain event is created

### US-005: Revoke License

As a content publisher, I want to revoke a license so that future access is prevented.

#### Acceptance Criteria

- Status becomes revoked
- Blockchain event is recorded
- Access is denied afterwards

### US-006: View License

As an administrator, I want to view license information so that I can troubleshoot access issues.

#### Acceptance Criteria

- License endpoint exists
- License history is visible
- Current status is returned

## Epic 3: Protected Content

### US-007: Retrieve Protected Content

As a licensed user, I want to access protected content so that I can consume purchased resources.

#### Acceptance Criteria

- Active license is required
- Matching content license is required
- Content is returned on success

### US-008: Prevent Access Without License

As a system, I want to reject unauthorized requests so that protected content remains controlled.

#### Acceptance Criteria

- HTTP 403 is returned
- Access event is not recorded
- Error message is returned

### US-009: Prevent Access With Revoked License

As a system, I want revoked licenses to fail validation so that previously removed rights are enforced.

#### Acceptance Criteria

- Revoked license is rejected
- HTTP 403 is returned
- Audit entry is created

## Epic 4: Auditing

### US-010: Record Access Event

As a publisher, I want content access recorded so that I have an audit trail.

#### Acceptance Criteria

- Access event is added to blockchain
- Timestamp is recorded
- User is recorded

### US-011: View Access History

As an administrator, I want to view license activity so that I can investigate usage.

#### Acceptance Criteria

- Query by license
- Query by user
- Events are sorted chronologically

## Epic 5: Demonstration Features

### US-012: View Blockchain

As a developer, I want to see all blocks so that I can understand the chain behavior.

#### Acceptance Criteria

- Endpoint returns chain
- Blocks are visible in order
- Hash values are visible

### US-013: Simulate Tampering

As a developer, I want to modify a stored block so that validation failures can be demonstrated.

#### Acceptance Criteria

- Test endpoint is available
- Blockchain validation fails
- Failure is clearly reported

### US-014: Download Limit DRM

As a publisher, I want a license to have a maximum download count so that usage restrictions can be demonstrated.

#### Acceptance Criteria

- Limit is stored on license
- Access events are counted
- Further requests are rejected once the limit is reached
