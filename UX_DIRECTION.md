# UX Direction: DRM Blockchain Demonstrator

## Product intent

This interface is a lightweight operations dashboard for a blockchain-powered DRM prototype. It should communicate trust, auditability, and denial logic without pretending to be a production media platform. The design should feel like a developer demo or internal audit console: clear, technical, and intentionally minimal.

## Design principles

- Educational clarity over polished consumer branding
- High contrast for status signals: valid vs revoked vs expired
- Audit-first layout that surfaces chain integrity and license decisions
- Strong visual distinction between safe access and denied access
- Mobile-friendly stack so the demo still works in a browser and on small screens

## Core user journey

1. View the current system state at a glance
2. Inspect one license and its validity window
3. Check whether the blockchain ledger is still tamper-free
4. Attempt protected content access using a license ID
5. Review the access verdict and ledger-backed reason

## Screen 1: Overview dashboard

Purpose: give the operator an immediate read on the whole system.

Primary elements:

- Summary cards for total licenses, active licenses, revoked licenses, and chain health
- A compact list of recent blockchain events
- A short warning or advisory if a license is expired or revoked

Visual treatment:

- Dark neutral UI with accent colors for status
- Successful or valid states use teal/green
- Revoked or denied states use red/orange
- Warning states use amber
- Hash values and timestamps should use monospace styling for technical clarity

## Screen 2: License ledger

Purpose: show the state of each license and allow quick review of why access is allowed or denied.

Primary elements:

- License row list with ID, content, owner, expiry, and status pill
- Detail panel on selection with dates, status reason, and relevant blockchain event reference
- Short list of recent events associated with that license

Recommended behaviors:

- Selecting a license updates the detail panel without leaving the page
- Status pills should remain highly readable at a glance
- Expired and revoked states should be visually distinct and not mistaken for normal operation

## Screen 3: Chain integrity and audit view

Purpose: make the blockchain feel real and torsion-free while staying understandable to non-blockchain users.

Primary elements:

- Block count and validation status
- Most recent block metadata
- Hash linkage and previous-hash trace
- A small note explaining that tampering would invalidate the chain

## Screen 4: Protected content access flow

Purpose: simulate the permission gate before content is delivered.

Primary elements:

- License ID and content ID inputs
- Access result banner with success or denial message
- A short explanation of the decision path: license status, expiry, blockchain validation, and audit record
- Access log showing whether the request was allowed or denied

Recommended logic in the prototype:

- Active license + valid chain = content granted
- Revoked license = content denied
- Expired license = content denied
- Tampered chain = validation warning and denial flow

## Frontend flow

- Dashboard loads with default metrics and sample licenses
- User selects a license or enters a license ID
- Chain validation can be triggered manually to simulate verification
- User requests protected content
- The access result updates the status banner and logs the event
- The UI reinforces the chain + license model without exposing deep backend mechanics

## Brief alignment notes

This direction stays aligned with the brief by emphasizing:

- educational clarity
- minimal implementation scope
- auditability over production realism
- license validation and access denial flows
- chain integrity as a visible concept

## Implementation notes for the frontend developer

- Keep the prototype as a single-page dashboard with a dark technical theme
- Use real sample data to demonstrate valid, revoked, and expired licenses
- Show hash values in a monospace font and maintain consistent status colors
- Validate UI states on the client side to make the demo easy to understand without a full backend
- Ensure buttons and form controls are keyboard-accessible and responsive on smaller screens
