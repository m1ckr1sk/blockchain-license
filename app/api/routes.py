from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from app.drm.models import LicenseCreateRequest

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/licenses")
def get_licenses(request: Request) -> dict[str, Any]:
    return {"licenses": list(request.app.state.drm_service.licenses.values())}


@router.get("/licenses/{license_id}")
def get_license(request: Request, license_id: str) -> dict[str, Any]:
    license = request.app.state.drm_service.licenses.get(license_id)
    if license is None:
        raise HTTPException(status_code=404, detail=f"License {license_id} not found.")
    return license


@router.get("/blockchain")
def get_blockchain(request: Request) -> dict[str, Any]:
    return {"blocks": request.app.state.blockchain.chain}


@router.get("/blockchain/validate")
def validate_blockchain(request: Request) -> dict[str, Any]:
    return request.app.state.blockchain.validate_chain()


@router.post("/blockchain/tamper")
def tamper_blockchain(request: Request) -> dict[str, Any]:
    return request.app.state.blockchain.tamper_last_block()


@router.post("/licenses", status_code=201)
def create_license(request: Request, payload: LicenseCreateRequest) -> dict[str, Any]:
    drm_service = request.app.state.drm_service
    license = drm_service.issue_license(payload.userId, payload.contentId, payload.expiresAt)
    return license


@router.post("/licenses/{license_id}/revoke")
def revoke_license(request: Request, license_id: str) -> dict[str, Any]:
    drm_service = request.app.state.drm_service

    try:
        license = drm_service.revoke_license(license_id)
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return license


@router.get("/content/{content_id}")
def get_content(request: Request, content_id: str, license_id: str = Query(..., alias="licenseId")) -> dict[str, Any]:
    drm_service = request.app.state.drm_service

    is_valid, reason = drm_service.validate_access(license_id, content_id)
    if not is_valid:
        drm_service.record_access_event(license_id, content_id, False, reason)
        raise HTTPException(status_code=403, detail=f"Access denied: {reason}")

    content = drm_service.get_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")

    drm_service.record_access_event(license_id, content_id, True, reason)
    return {
        "contentId": content["contentId"],
        "title": content["title"],
        "body": content["body"],
        "licenseId": license_id,
        "status": "GRANTED",
    }
