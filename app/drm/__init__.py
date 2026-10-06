"""License and content access logic for the DRM demonstrator."""

from .models import LicenseCreateRequest, LicenseRecord
from .service import DRMService

__all__ = ["DRMService", "LicenseCreateRequest", "LicenseRecord"]
