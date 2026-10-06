# Contributing Guide

## Scope

This project is a small educational proof-of-concept for using a blockchain ledger to govern access to protected content. Contributions should keep the implementation understandable, testable, and aligned with the project brief.

## Development Principles

### 1. Keep the model simple and explicit

This is not a production DRM platform. Code should favor clarity over complexity. Prefer explicit data models and straightforward validation flows over abstract frameworks or over-engineered patterns.

### 2. Treat the blockchain as a demonstrator

The implementation should validate the idea of immutable event records and integrity checking, not simulate a full distributed ledger system. Keep the logic deterministic and easy to follow.

### 3. Prioritize correctness over cleverness

Each license check, expiry check, and chain validation should be easy to reason about. Avoid hidden side effects or magic behavior in API routes or repository logic.

### 4. Maintain auditable behavior

If a license is created, revoked, or used, the event should be traceable. Logs and blockchain events should reflect the actual state transition in a clear way.

## Local Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic pytest
   ```

3. Run the app locally:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Code Standards

- Use Python 3.12-compatible syntax and typing where helpful.
- Keep functions focused and small.
- Name models and functions in a way that matches the domain language: license, block, chain, validation, access record.
- Prefer explicit status values such as `ACTIVE`, `REVOKED`, and `EXPIRED`.
- Validate all user input through Pydantic models or equivalent API-level validation.
- Document any behavior that is intentionally simplified for educational purposes.

## Testing Expectations

- Add or update tests for all bug fixes and new features.
- Cover the main rule flows:
  - valid access succeeds
  - unauthorized access fails
  - revoked access fails
  - expired access fails
  - chain tampering is detected
- Prefer focused tests over broad mock-heavy tests.
- Keep test names descriptive and behavior-oriented.

## Security and Ethics

- Do not commit secrets, private keys, or deployment credentials.
- Treat the demo as educational, not as a complete protection mechanism.
- Ensure the app communicates clearly that this is a demonstrator and not a production DRM control system.
- Avoid encouraging clients to assume that content delivery security is guaranteed at the client side.

## Pull Request Guidance

Before opening a PR:

- Update documentation when behavior changes
- Ensure tests pass
- Keep the scope narrow and well described
- Explain the reasoning behind any blockchain-related logic change
- Include clear acceptance criteria or examples when adding features

## Commit Guidance

Use concise, descriptive commit messages. Prefer messages such as:

- `add genesis block validation`
- `implement license revocation flow`
- `add protected content access tests`

## Review Expectations

Reviewers should check for:

- code clarity and maintainability
- correctness of blockchain validation logic
- realistic license-state handling
- test coverage for security-sensitive flows
- alignment with the project brief and scope

## When in Doubt

Keep the implementation simple, readable, and educational. This project is best served by a clear demonstration of the core concept rather than by production-grade complexity.
