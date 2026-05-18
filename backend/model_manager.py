"""Discover installed models and (optionally) download recommended ones.
Downloads are GATED by SETTINGS.airgapped — if true, no outbound traffic at all.
"""
from __future__ import annotations
import asyncio, hashlib, json
from pathlib import Path
import httpx
from config import MODELS_DIR, SETTINGS, CACHE_DIR

EXT_CKPT = {".safetensors", ".ckpt", ".gguf"}
EXT_LORA = {".safetensors", ".pt"}

RECOMMENDED = {
    "sdxl_base": {
        "subdir": "checkpoints",
        "filename": "sd_xl_base_1.0.safetensors",
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b",
    },
    "flux_schnell": {
        "subdir": "checkpoints",
        "filename": "flux1-schnell.safetensors",
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors",
        "sha256": None,
    },
    "realvis_xl": {
        "subdir": "checkpoints",
        "filename": "realvisxlV40.safetensors",
        "url": "https://huggingface.co/SG161222/RealVisXL_V4.0/resolve/main/RealVisXL_V4.0.safetensors",
        "sha256": None,
    },
    "anime_xl": {
        "subdir": "checkpoints",
        "filename": "animagineXL31.safetensors",
        "url": "https://huggingface.co/cagliostrolab/animagine-xl-3.1/resolve/main/animagine-xl-3.1.safetensors",
        "sha256": None,
    },
    "esrgan": {
        "subdir": "upscale_models",
        "filename": "RealESRGAN_x4plus.pth",
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "sha256": None,
    },
    "animatediff": {
        "subdir": "animatediff_models",
        "filename": "mm_sd_v15_v2.ckpt",
        "url": "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt",
        "sha256": None,
    },
}


def list_installed() -> dict:
    def scan(dir_: Path, exts: set[str]) -> list[str]:
        if not dir_.exists(): return []
        return sorted(p.name for p in dir_.iterdir() if p.suffix.lower() in exts and p.is_file())
    return {
        "checkpoints": scan(MODELS_DIR / "checkpoints", EXT_CKPT),
        "loras": scan(MODELS_DIR / "loras", EXT_LORA),
        "vaes": scan(MODELS_DIR / "vaes", EXT_CKPT),
        "upscalers": scan(MODELS_DIR / "upscale_models", {".pth", ".bin", ".safetensors"}),
    }


async def download_recommended(model_id: str, progress_cb=None) -> Path:
    if SETTINGS.airgapped:
        raise RuntimeError("Airgapped mode is enabled — downloads are disabled in Settings.")
    info = RECOMMENDED[model_id]
    target = MODELS_DIR / info["subdir"] / info["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")

    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as c:
        async with c.stream("GET", info["url"]) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length") or 0)
            done = 0
            h = hashlib.sha256()
            with tmp.open("wb") as f:
                async for chunk in r.aiter_bytes(chunk_size=1 << 20):
                    f.write(chunk); h.update(chunk); done += len(chunk)
                    if progress_cb and total:
                        await progress_cb(done / total)
    # Verify hash if provided
    if info.get("sha256"):
        if h.hexdigest() != info["sha256"]:
            tmp.unlink(missing_ok=True)
            raise RuntimeError("SHA256 mismatch — download corrupt or tampered with")
    tmp.replace(target)
    return target
