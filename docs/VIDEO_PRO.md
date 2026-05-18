# Video Pro Mode

LocalForge ships with a built-in image generator (DirectML) that runs on any modern GPU. **Video Pro** is an optional second backend that adds **photorealistic AI video generation** using state-of-the-art CUDA-only models — LTX-Video, Wan 2.1, and Hunyuan Video — running locally on AMD GPUs through ZLUDA.

## Why a separate backend?

The image backend uses **torch-directml**, which is the most compatible PyTorch backend for AMD on Windows but doesn't support the operators the newest video models depend on (flash attention variants, custom CUDA kernels, etc.).

ZLUDA is a CUDA-on-AMD shim that runs a CUDA-built PyTorch on Radeon hardware. It's amazing for video, but installing it changes a lot of low-level DLLs — so LocalForge keeps it in a fully isolated second backend that only runs when you ask it to. Your image workflow stays untouched.

The two backends run on different ports (`8188` for images, `8189` for video), and the app routes each job to the correct one automatically.

## Hardware requirements

- **AMD RX 7900 XT** (recommended) or any RDNA3 card with ≥ 16 GB VRAM
- **RDNA2 (RX 6800/6900)** also works but Hunyuan will be tight on 16 GB cards
- **Nvidia users**: ZLUDA isn't needed — open an issue and we'll wire native CUDA in (the same backend works, just without the shim)
- **Disk**: ~6 GB for the backend, plus 4–25 GB per video model you download
- **RAM**: 16 GB minimum, 32 GB recommended

## Installation

1. Open LocalForge.
2. Click **Video Pro** in the sidebar (look for the violet PRO badge).
3. Click **Install Video Pro**.
4. Wait ~5–15 minutes. The live install log streams in the right panel so you can see exactly what's happening:
   - Downloads an embeddable Python 3.11
   - Downloads [ZLUDA v3](https://github.com/lshqqytiger/ZLUDA) (~30 MB)
   - Downloads CUDA-built PyTorch (~2.5 GB)
   - Clones a second isolated ComfyUI
   - Installs VideoHelperSuite, LTXVideo, WanVideoWrapper, HunyuanVideoWrapper
   - Verifies `torch.cuda.is_available() == True` (through ZLUDA)
5. Pick a model to download (LTX is the smallest and fastest — start there).
6. Generate.

## The three models

| Model           | Download  | Resolution | Frames | Avg time (7900 XT) | When to use                                |
| --------------- | --------- | ---------- | ------ | ------------------ | ------------------------------------------ |
| **LTX-Video**   | 4.5 GB    | 768×512    | 121    | ~45s               | Iterating, drafts, social content          |
| **Wan 2.1 T2V** | 5.2 GB    | 832×480    | 81     | ~90s               | The sweet spot — best quality/time balance |
| **Hunyuan**     | 25 GB     | 1280×720   | 129    | ~6 min             | Final renders, hero shots, max fidelity    |

All three are open-weight. Sources:

- LTX-Video: [Lightricks/LTX-Video](https://huggingface.co/Lightricks/LTX-Video)
- Wan 2.1: [Wan-AI/Wan2.1-T2V-1.3B](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B)
- Hunyuan Video: [Kijai/HunyuanVideo_comfy](https://huggingface.co/Kijai/HunyuanVideo_comfy)

## Using Video Pro

The Video Pro page works like the image page, with a few additions:

1. **Pick a model** (three cards across the top — LTX / Wan / Hunyuan)
2. **Pick a style preset** (Photorealistic / Cinematic / Animation / Documentary)
3. **Write your prompt** — be descriptive about motion ("camera slowly pans left", "subject walks forward")
4. **Click Generate**

Output is `.mp4` (with `.gif` previews in the gallery). Hover any video tile in the gallery to play it back inline.

### Prompting tips

- **Describe motion explicitly**: "a koi fish swimming, camera follows from above"
- **Avoid contradictions**: don't ask for both "static shot" and "dolly zoom"
- **Reference style**: "shot on 35mm film", "anime cel-shaded", "documentary handheld"
- **Keep prompts under 75 tokens** for LTX, ~150 for Wan/Hunyuan

## How the dual-backend actually works

```
┌─────────────────────────────────────┐
│   LocalForge (Tauri + React)        │
└──────────────┬──────────────────────┘
               │ FastAPI :8000
               ▼
        ┌──────────────┐
        │ backends.py  │  routes by job mode
        └──────┬───────┘
        ┌─────┴─────┐
        ▼           ▼
┌──────────────┐  ┌────────────────┐
│ ComfyUI      │  │ ComfyUI (video)│
│ DirectML     │  │ ZLUDA + CUDA   │
│ port 8188    │  │ port 8189      │
│ images       │  │ video          │
└──────────────┘  └────────────────┘
```

- `BackendManager.start_all()` launches whichever backends are installed
- `route_port(mode)` returns 8188 for image jobs, 8189 for `txt2vid` / `img2vid` (only if Video Pro is installed and enabled in settings)
- `/api/health` returns the live status of both backends — the sidebar pills you see in the app come from there

## Disabling / uninstalling Video Pro

- **Disable temporarily**: Settings → Video Pro → toggle off. The backend won't launch on next startup.
- **Uninstall completely**: delete `%APPDATA%\LocalForge\comfyui_video\`, `python_video\`, and `zluda\`. About 6 GB freed.

You can always reinstall from the Video Pro tab — your image backend is untouched.

## Troubleshooting

**"torch.cuda.is_available() returned False"**
ZLUDA didn't load. Check that `backend/zluda/nvcuda.dll` exists and that your AMD driver is up to date (Adrenalin 24.x+).

**"Out of memory" on Hunyuan**
You probably have a 16 GB card. Drop to Wan 2.1, or set Video Pro → Memory mode = "Low VRAM" in Settings (uses tiled VAE + CPU offload, ~2x slower but works on 12 GB).

**Video backend won't start**
Open Settings → Backend status. If `video` shows an error, click "View install log". Most common cause is an interrupted download — just click Install again, it resumes.

**"My image generator slowed down after installing Video Pro"**
Shouldn't happen — they're isolated. If it does, toggle Video Pro off in Settings and restart. Open an issue with your `%APPDATA%\LocalForge\logs\` folder attached.
