from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.blockchain.service import BlockchainService
from app.drm.models import LicenseRecord


class DRMService:
    def __init__(self, blockchain: BlockchainService) -> None:
        self.blockchain = blockchain
        self.licenses: dict[str, dict[str, Any]] = {}
        self.content_store: dict[str, dict[str, Any]] = {
            "content-001": {
                "contentId": "content-001",
                "title": "Protected Market Report",
                "body": "This protected content is only accessible to valid license holders.",
            },
            "content-002": {
                "contentId": "content-002",
                "title": "API Access License Demo",
                "body": "Educational example content for the DRM demonstrator.",
            },
            "content-003": {
                "contentId": "content-003",
                "title": "Expired Content Sample",
                "body": "This content is meant to demonstrate expiration handling.",
            },
            "content-004": {
                "contentId": "content-004",
                "title": "Audit Trail Example",
                "body": "This record demonstrates successful access and blockchain auditing.",
            },
            "course-module-01": {
                "contentId": "course-module-01",
                "title": "Course Module 01",
                "body": "This learning module is protected behind the valid license flow.",
            },
        }

    def issue_license(self, user_id: str, content_id: str, expires_at: datetime) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        license_id = f"LIC-{uuid4().hex[:8].upper()}"
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        status = "ACTIVE" if expires_at > now else "EXPIRED"
        license = LicenseRecord(
            licenseId=license_id,
            userId=user_id,
            contentId=content_id,
            issuedAt=now,
            expiresAt=expires_at,
            status=status,
        )

        self.licenses[license_id] = license.model_dump(mode="json")
        self.blockchain.add_block(
            {
                "type": "LICENSE_ISSUED",
                "licenseId": license_id,
                "userId": user_id,
                "contentId": content_id,
                "expiresAt": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": status,
            }
        )
        return self.licenses[license_id]

    def revoke_license(self, license_id: str) -> dict[str, Any]:
        license = self.licenses.get(license_id)
        if not license:
            raise KeyError(f"License {license_id} not found.")

        license["status"] = "REVOKED"
        self.blockchain.add_block(
            {
                "type": "LICENSE_REVOKED",
                "licenseId": license_id,
                "userId": license["userId"],
                "contentId": license["contentId"],
            }
        )
        return license

    def validate_access(self, license_id: str, content_id: str) -> tuple[bool, str]:
        blockchain_validation = self.blockchain.validate_chain()
        if not blockchain_validation.get("valid", False):
            return False, "BLOCKCHAIN_TAMPERED"

        license = self.licenses.get(license_id)
        if not license:
            return False, "LICENSE_NOT_FOUND"

        if license["contentId"] != content_id:
            return False, "CONTENT_MISMATCH"

        status = license["status"]
        if status == "REVOKED":
            return False, "LICENSE_REVOKED"
        if status == "EXPIRED":
            return False, "LICENSE_EXPIRED"

        expires_at = datetime.fromisoformat(license["expiresAt"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            license["status"] = "EXPIRED"
            self.blockchain.add_block(
                {
                    "type": "LICENSE_EXPIRED",
                    "licenseId": license_id,
                    "userId": license["userId"],
                    "contentId": content_id,
                }
            )
            return False, "LICENSE_EXPIRED"

        return True, "ACCESS_GRANTED"

    def record_access_event(self, license_id: str, content_id: str, granted: bool, reason: str) -> dict[str, Any]:
        event = {
            "type": "CONTENT_ACCESS",
            "licenseId": license_id,
            "contentId": content_id,
            "result": "GRANTED" if granted else "DENIED",
            "reason": reason,
        }
        return self.blockchain.add_block(event)

    def get_content(self, content_id: str) -> dict[str, Any] | None:
        return self.content_store.get(content_id)
