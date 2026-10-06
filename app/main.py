from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.blockchain.service import BlockchainService
from app.drm.service import DRMService

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="FastAPI DRM Blockchain Demonstrator",
    description="Educational example of blockchain-backed license validation for protected content.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.blockchain = BlockchainService()
app.state.drm_service = DRMService(app.state.blockchain)
app.include_router(router)
app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")
