"""Central configuration. All paths are resolved relative to LOCALFORGE_DATA_DIR
so portable and per-user installs both work transparently."""
from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict, field
from pathlib import Path

DATA_DIR = Path(os.environ.get("LOCALFORGE_DATA_DIR", Path.home() / ".localforge")).resolve()
RESOURCE_DIR = Path(os.environ.get("LOCALFORGE_RESOURCE_DIR", Path(__file__).parent.parent)).resolve()

MODELS_DIR = DATA_DIR / "models"
OUTPUT_DIR = DATA_DIR / "output"
CACHE_DIR = DATA_DIR / "cache"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "localforge.db"
SETTINGS_PATH = DATA_DIR / "settings.json"

for sub in ("checkpoints", "loras", "vaes", "upscale_models", "controlnet",
            "animatediff_models", "clip", "clip_vision", "embeddings"):
    (MODELS_DIR / sub).mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Settings:
    save_sidecar: bool = True
    output_format: str = "png"          # png | jpg | webp
    vram_mode: str = "balanced"         # speed | balanced | lowvram
    auto_update: bool = True
    airgapped: bool = False             # if True, ALL outbound HTTPS is refused
    comfyui_port: int = 8188
    comfyui_video_port: int = 8189
    api_port: int = 8765
    keep_intermediates: bool = False
    video_pro_enabled: bool = True      # Route video jobs to ZLUDA backend
    video_default_model: str = "ltx"    # ltx | wan21 | hunyuan | animatediff


def load_settings() -> Settings:
    if SETTINGS_PATH.exists():
        try:
            return Settings(**{**asdict(Settings()), **json.loads(SETTINGS_PATH.read_text())})
        except Exception:
            pass
    return Settings()


def save_settings(s: Settings) -> None:
    SETTINGS_PATH.write_text(json.dumps(asdict(s), indent=2))


SETTINGS = load_settings()
