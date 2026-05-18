from fastapi import APIRouter
from dataclasses import asdict
from config import SETTINGS, save_settings, Settings
from gpu_detect import detect

router = APIRouter()


@router.get("/api/settings")
async def get_settings():
    return asdict(SETTINGS)


@router.post("/api/settings")
async def update_settings(payload: dict):
    new = Settings(**{**asdict(SETTINGS), **payload})
    save_settings(new)
    for k, v in asdict(new).items():
        setattr(SETTINGS, k, v)
    return asdict(SETTINGS)


@router.get("/api/gpu")
async def gpu_info():
    g = detect()
    return {
        "detected": g.detected, "name": g.name, "vram_gb": g.vram_gb,
        "backend": g.backend, "recommended_vram_mode": g.recommended_vram_mode,
    }
