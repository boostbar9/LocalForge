"""Automatic GPU detection and recommendation.

Strategy on Windows:
1. Try `torch_directml`. If it imports and reports a device, that's our backend.
2. Else parse `wmic path Win32_VideoController` to identify the GPU and VRAM.
3. Special-case the AMD RX 7900 XT (20 GB) — apply aggressive memory presets.
"""
from __future__ import annotations
import re, subprocess
from dataclasses import dataclass


@dataclass
class GPUInfo:
    detected: bool
    name: str
    vram_gb: int
    backend: str         # "directml" | "cpu"
    recommended_vram_mode: str   # speed | balanced | lowvram


def _wmic_gpu() -> tuple[str, int]:
    try:
        out = subprocess.check_output(
            ["wmic", "path", "Win32_VideoController", "get", "Name,AdapterRAM", "/format:csv"],
            stderr=subprocess.DEVNULL, timeout=4, text=True,
        )
        best_name, best_vram = "Unknown GPU", 0
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 3 and parts[1].isdigit():
                ram = int(parts[1])
                name = parts[2]
                if ram > best_vram:
                    best_vram, best_name = ram, name
        return best_name, best_vram // (1024 ** 3)
    except Exception:
        return "Unknown GPU", 0


def detect() -> GPUInfo:
    name, vram = _wmic_gpu()
    backend = "cpu"
    try:
        import torch_directml  # type: ignore
        if torch_directml.device_count() > 0:
            backend = "directml"
            dml_name = torch_directml.device_name(0)
            if dml_name:
                name = dml_name
    except Exception:
        pass

    # Special-case RX 7900 XT: 20 GB lets us run SDXL + Flux at high res easily.
    is_7900 = "7900 XT" in name or vram >= 20
    if is_7900:
        mode = "speed"
    elif vram >= 12:
        mode = "balanced"
    elif vram >= 6:
        mode = "lowvram"
    else:
        mode = "lowvram"

    return GPUInfo(
        detected=backend != "cpu",
        name=name or "Unknown GPU",
        vram_gb=max(vram, 0),
        backend=backend,
        recommended_vram_mode=mode,
    )


def comfyui_launch_args(gpu: GPUInfo) -> list[str]:
    """ComfyUI CLI flags tuned for the detected hardware."""
    args = ["--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch"]

    if gpu.backend == "directml":
        # ComfyUI's built-in DirectML flag — selects torch-directml backend.
        args += ["--directml"]
    elif gpu.backend == "cpu":
        args += ["--cpu"]

    # VRAM tuning
    if gpu.recommended_vram_mode == "speed":
        # 20 GB cards: keep models resident, big preview, fp16 everywhere
        args += ["--highvram", "--preview-method", "auto", "--fp16-unet", "--fp16-vae"]
    elif gpu.recommended_vram_mode == "balanced":
        args += ["--normalvram", "--preview-method", "auto"]
    else:
        args += ["--lowvram", "--preview-method", "latent2rgb"]

    return args
