# GPU Optimization — AMD RX 7900 XT

LocalForge uses **DirectML** as the AMD acceleration layer on Windows. DirectML
is Microsoft's hardware-agnostic ML runtime — it works on every Windows GPU
without ROCm, without WSL, and without Linux.

## Why DirectML (vs ZLUDA, ROCm, etc.)

| Backend | Setup | Speed on 7900 XT | Stability |
|---|---|---|---|
| **DirectML** ✅ chosen | Zero — install and go | ~1.7 it/s SDXL | Very high |
| ZLUDA (CUDA translation) | Manual DLL setup | ~2.6 it/s SDXL | Medium — model crashes vary |
| ROCm | Linux/WSL only | ~3.0 it/s SDXL | Linux required |
| CPU fallback | n/a | ~0.02 it/s | n/a |

For a consumer one-click app, DirectML is the right trade-off for images. **For video**, the math is different — modern photoreal video models (LTX, Wan 2.1, Hunyuan) require operators DirectML doesn't support, so LocalForge ships a second, isolated **Video Pro** backend that uses ZLUDA. It's a one-click install from inside the app and doesn't touch your image backend at all. See [VIDEO_PRO.md](VIDEO_PRO.md) for the full story.

> TL;DR: **images = DirectML (default, always on). video = ZLUDA (opt-in from the Video Pro tab).**

## Built-in optimizations for the RX 7900 XT

LocalForge detects 20 GB VRAM and **automatically** applies:

```python
# backend/gpu_detect.py — comfyui_launch_args()
[
  "--directml",
  "--highvram",          # keep models resident
  "--preview-method", "auto",
  "--fp16-unet",         # half precision UNet
  "--fp16-vae",          # half precision VAE
]
```

You can override these in **Settings → VRAM mode**.

## Recommended Adrenalin settings

Open AMD Adrenalin → Gaming → LocalForge.exe (it should appear after first run):

| Setting | Value | Why |
|---|---|---|
| Anti-lag | Off | Compute-only, no rendering benefit |
| Radeon Boost | Off | Same reason |
| Radeon Chill | Off | Don't throttle our compute |
| Image Sharpening | Off | Irrelevant |
| Tessellation | App-controlled | — |
| Power profile | High Performance | Sustained clocks |

For **Global Tuning**:
- Custom GPU clock: leave at default unless you know what you're doing
- Memory tuning: a small +50–100 MHz on VRAM gives 2-4% diffusion speedup

## Troubleshooting

### Backend reports `cpu` instead of `directml`

Open a terminal and run:

```powershell
cd %ProgramFiles%\LocalForge\backend
python\python.exe -c "import torch_directml; print(torch_directml.device_count(), torch_directml.device_name(0))"
```

Expected output:
```
1 AMD Radeon RX 7900 XT
```

If you see `0` or an ImportError:
1. Update your AMD Adrenalin driver to 24.4.1 or newer.
2. Update Windows 11 to 23H2+.
3. In LocalForge: **Settings → Repair GPU backend** (runs `install_directml.py`).

### Black images / instant completion

Lower VRAM mode to **Balanced** — DirectML can silently fail to allocate at extreme batch sizes.

### Generation is slow (under 1 it/s)

- Close other GPU consumers (browsers with hardware accel, games).
- Check **Task Manager → Performance → GPU** — the dedicated memory bar should climb to ~12-16 GB during generation.
- Make sure `--fp16-unet` is enabled (Settings → VRAM mode = Speed).
