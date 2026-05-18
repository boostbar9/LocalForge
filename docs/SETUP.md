# Step-by-Step Setup Guide

For end users on Windows 11 with an AMD RX 7900 XT.

## Option A — Installer (recommended)

1. **Download** `LocalForge-Setup-1.0.0.exe` from the Releases page.
2. **Right-click → Run as administrator.** (Required only once, to install Program Files.)
3. Click **Next → Install**. The installer:
   - Extracts the app to `C:\Program Files\LocalForge\`
   - Creates a Start Menu and Desktop shortcut
   - Launches `bootstrap.py`, which downloads ComfyUI (~150 MB) and the DirectML PyTorch build (~700 MB)
4. When the installer finishes, double-click **LocalForge** on the desktop.
5. On the **Welcome** screen, click **Pick your first model**.
6. Click **Get** next to **Stable Diffusion XL 1.0 base** (≈ 7 GB). Wait for it to finish.
7. Go to **Generate**, type a prompt, click **Generate**. First image takes ~30 s while the model loads into VRAM; subsequent images take ~10 s.

## Option B — Portable

1. Download `LocalForge-1.0.0-portable.zip`.
2. Extract anywhere — a USB drive, an SSD, your Desktop.
3. Double-click `LocalForge.exe` inside the folder. No admin needed.
4. The presence of `portable.txt` in the same folder tells LocalForge to store everything (models, output, settings) under `localforge_data\` next to the EXE — nothing touches the registry or `%APPDATA%`.

## Verifying everything works

In LocalForge, open **Settings → Hardware**. You should see:

```
GPU: AMD Radeon RX 7900 XT
VRAM: 20 GB
Backend: directml
Detected: ✓
```

If `Backend: cpu` shows up, see [GPU_OPTIMIZATION.md](GPU_OPTIMIZATION.md#troubleshooting).

## First generation checklist

- [ ] At least one checkpoint in `models/checkpoints/` (SDXL base is fine)
- [ ] Backend status (bottom of sidebar) shows green
- [ ] Settings → Hardware shows DirectML detected
- [ ] Type a prompt like: `a photo of an orange tabby cat on a windowsill at golden hour`
- [ ] Style: Photorealistic · Quality: Balanced · Size: Square 1024
- [ ] Click **Generate**

Your first image lands in the Gallery in 30-40 seconds.
