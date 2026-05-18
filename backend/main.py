"""LocalForge backend entry point.

Supervises two ComfyUI subprocesses (image + optional video pro), exposes a
FastAPI service on 127.0.0.1:8765, and tears everything down on exit.
"""
from __future__ import annotations
import asyncio, atexit, signal, sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(0, str(Path(__file__).parent))

from config import SETTINGS
from backends import MANAGER
from api import generate, gallery, models, settings as settings_api, ws, video
from workflow_runner import worker_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MANAGER.start_all()
    asyncio.create_task(worker_loop())
    yield
    MANAGER.stop_all()


app = FastAPI(title="LocalForge", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://tauri.localhost", "tauri://localhost"],
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    statuses = MANAGER.status()
    return {
        "status": "ok",
        "backends": [s.__dict__ for s in statuses],
    }


app.include_router(generate.router)
app.include_router(gallery.router)
app.include_router(models.router)
app.include_router(settings_api.router)
app.include_router(ws.router)
app.include_router(video.router)


def _cleanup(*_):
    MANAGER.stop_all()


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, _cleanup)
if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, _cleanup)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SETTINGS.api_port, log_level="warning")
