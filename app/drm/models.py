from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class LicenseCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    userId: str
    contentId: str
    expiresAt: datetime

    @field_validator("expiresAt", mode="before")
    @classmethod
    def parse_expires_at(cls, value):
        if isinstance(value, str):
            value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        return value


class LicenseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    licenseId: str
    userId: str
    contentId: str
    issuedAt: datetime
    expiresAt: datetime
    status: Literal["ACTIVE", "REVOKED", "EXPIRED"] = "ACTIVE"
