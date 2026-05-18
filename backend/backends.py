"""Dual-backend manager.

LocalForge runs TWO ComfyUI processes side-by-side:

  • image_backend  → DirectML, port 8188  (fast, bulletproof, AMD-safe)
  • video_backend  → ZLUDA + CUDA torch, port 8189  (real photoreal video)

Jobs are routed by mode:
  txt2img / img2img / inpaint / upscale  → image_backend
  txt2vid / img2vid                       → video_backend (if installed)

The video backend is OPTIONAL — if ZLUDA isn't installed yet, video jobs
gracefully fall back to AnimateDiff on the image backend.
"""
from __future__ import annotations
import asyncio, os, subprocess, sys
from dataclasses import dataclass
from pathlib import Path
from config import SETTINGS, RESOURCE_DIR, LOG_DIR, MODELS_DIR, OUTPUT_DIR
from gpu_detect import detect, comfyui_launch_args

BACKEND_DIR = RESOURCE_DIR / "backend"
COMFY_IMAGE_DIR = BACKEND_DIR / "comfyui"
COMFY_VIDEO_DIR = BACKEND_DIR / "comfyui_video"
PY_IMAGE = BACKEND_DIR / "python" / "python.exe"
PY_VIDEO = BACKEND_DIR / "python_video" / "python.exe"
ZLUDA_DIR = BACKEND_DIR / "zluda"

IMAGE_PORT = 8188
VIDEO_PORT = 8189


@dataclass
class BackendStatus:
    name: str
    port: int
    available: bool
    running: bool
    backend_type: str       # "directml" | "zluda" | "cpu" | "missing"
    error: str | None = None


class BackendManager:
    def __init__(self) -> None:
        self.image_proc: subprocess.Popen | None = None
        self.video_proc: subprocess.Popen | None = None

    # ------------------ image backend (DirectML) ------------------
    def start_image(self) -> None:
        if not COMFY_IMAGE_DIR.exists() or not PY_IMAGE.exists():
            return
        gpu = detect()
        args = [
            str(PY_IMAGE), str(COMFY_IMAGE_DIR / "main.py"),
            *comfyui_launch_args(gpu),
            "--port", str(IMAGE_PORT),
            "--output-directory", str(OUTPUT_DIR),
        ]
        log = (LOG_DIR / "comfyui_image.log").open("a")
        self.image_proc = subprocess.Popen(
            args, cwd=str(COMFY_IMAGE_DIR),
            stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

    # ------------------ video backend (ZLUDA + CUDA torch) ------------------
    def video_available(self) -> bool:
        return (COMFY_VIDEO_DIR.exists() and PY_VIDEO.exists() and
                ZLUDA_DIR.exists() and (ZLUDA_DIR / "nvcuda.dll").exists())

    def start_video(self) -> None:
        if not self.video_available():
            return
        # ZLUDA works by injecting CUDA shim DLLs into PATH ahead of system ones.
        env = os.environ.copy()
        env["PATH"] = f"{ZLUDA_DIR};{env.get('PATH','')}"
        env["HIP_VISIBLE_DEVICES"] = "0"
        env["ZLUDA_COMGR_LOG_LEVEL"] = "0"
        # Force fp16 + no flash attention (DirectML/ZLUDA both prefer this)
        args = [
            str(PY_VIDEO), str(COMFY_VIDEO_DIR / "main.py"),
            "--listen", "127.0.0.1", "--port", str(VIDEO_PORT),
            "--disable-auto-launch",
            "--output-directory", str(OUTPUT_DIR),
            "--highvram", "--fp16-unet", "--fp16-vae",
            "--use-pytorch-cross-attention",
        ]
        log = (LOG_DIR / "comfyui_video.log").open("a")
        self.video_proc = subprocess.Popen(
            args, cwd=str(COMFY_VIDEO_DIR), env=env,
            stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

    # ------------------ lifecycle ------------------
    async def wait_for(self, port: int, timeout: int = 120) -> bool:
        import httpx
        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout
        async with httpx.AsyncClient(timeout=2) as c:
            while loop.time() < deadline:
                try:
                    r = await c.get(f"http://127.0.0.1:{port}/system_stats")
                    if r.status_code == 200:
                        return True
                except Exception:
                    pass
                await asyncio.sleep(1)
        return False

    async def start_all(self) -> None:
        self.start_image()
        if self.video_available():
            self.start_video()
        await asyncio.gather(
            self.wait_for(IMAGE_PORT),
            self.wait_for(VIDEO_PORT) if self.video_available() else asyncio.sleep(0),
        )

    def stop_all(self) -> None:
        for proc in (self.image_proc, self.video_proc):
            if proc:
                try: proc.terminate()
                except Exception: pass

    def status(self) -> list[BackendStatus]:
        return [
            BackendStatus(
                name="Image (DirectML)", port=IMAGE_PORT,
                available=COMFY_IMAGE_DIR.exists(),
                running=self.image_proc is not None and self.image_proc.poll() is None,
                backend_type="directml" if detect().backend == "directml" else "cpu",
            ),
            BackendStatus(
                name="Video Pro (ZLUDA)", port=VIDEO_PORT,
                available=self.video_available(),
                running=self.video_proc is not None and self.video_proc.poll() is None,
                backend_type="zluda" if self.video_available() else "missing",
                error=None if self.video_available()
                      else "Install via Settings → Video Pro → Install ZLUDA",
            ),
        ]


def route_port(mode: str) -> int:
    """Return the ComfyUI port responsible for a given job mode."""
    video_modes = {"txt2vid", "img2vid", "vid2vid"}
    if mode in video_modes and SETTINGS.video_pro_enabled:
        return VIDEO_PORT
    return IMAGE_PORT


MANAGER = BackendManager()
