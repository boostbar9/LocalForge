"""Video Pro endpoints — install, status, model downloads."""
from __future__ import annotations
import asyncio, subprocess, sys
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backends import MANAGER

router = APIRouter()

INSTALL_LOG: list[str] = []
INSTALL_TASK: asyncio.Task | None = None


@router.get("/api/video/status")
async def status():
    s = next((b for b in MANAGER.status() if "Video" in b.name), None)
    if not s:
        return {"installed": False, "running": False}
    return {
        "installed": s.available,
        "running": s.running,
        "error": s.error,
    }


@router.post("/api/video/install")
async def install():
    global INSTALL_TASK
    if INSTALL_TASK and not INSTALL_TASK.done():
        return {"already_running": True}
    INSTALL_LOG.clear()

    async def run():
        script = Path(__file__).parent.parent / "scripts" / "install_video_pro.py"
        py = Path(__file__).parent.parent / "python" / "python.exe"
        proc = await asyncio.create_subprocess_exec(
            str(py), str(script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        async for line in proc.stdout:
            INSTALL_LOG.append(line.decode(errors="ignore").rstrip())
        await proc.wait()
        if proc.returncode == 0:
            MANAGER.start_video()
            await MANAGER.wait_for(8189, timeout=120)
        return proc.returncode

    INSTALL_TASK = asyncio.create_task(run())
    return {"started": True}


@router.get("/api/video/install/log")
async def install_log():
    return {
        "lines": INSTALL_LOG[-500:],
        "done": INSTALL_TASK is not None and INSTALL_TASK.done(),
    }


# Recommended video model downloads
VIDEO_MODELS = {
    "ltx_video": {
        "subdir": "checkpoints",
        "filename": "ltx-video-2b-v0.9.safetensors",
        "url": "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.safetensors",
        "name": "LTX-Video 2B (fast, ~60s per clip)",
        "size_gb": 4.5,
    },
    "wan21_t2v": {
        "subdir": "checkpoints",
        "filename": "Wan2.1-T2V-1.3B.safetensors",
        "url": "https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B/resolve/main/Wan2.1-T2V-1.3B.safetensors",
        "name": "Wan 2.1 T2V 1.3B (balanced quality, ~3 min)",
        "size_gb": 5.2,
    },
    "hunyuan_video": {
        "subdir": "checkpoints",
        "filename": "hunyuan_video_t2v_720p_bf16.safetensors",
        "url": "https://huggingface.co/Kijai/HunyuanVideo_comfy/resolve/main/hunyuan_video_t2v_720p_bf16.safetensors",
        "name": "HunyuanVideo 720p (Sora-grade, ~12 min)",
        "size_gb": 25.6,
    },
}


@router.get("/api/video/models")
async def list_video_models():
    return VIDEO_MODELS
