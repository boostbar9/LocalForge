# LocalForge AI

A fully local, one-click AI **image and video** generation app for Windows 11.
No cloud, no accounts, no telemetry. All models and processing stay on your machine.

![status](https://img.shields.io/badge/status-stable-brightgreen) ![version](https://img.shields.io/badge/version-1.1.0-blueviolet) ![platform](https://img.shields.io/badge/platform-Windows%2011-blue) ![gpu](https://img.shields.io/badge/GPU-AMD%20RX%207900%20XT-red)

## Highlights

- **One-click install** — single `.exe` installer, no Python or Git required by the user
- **100% offline** after first-run model download (or use Portable mode and copy models manually)
- **Dual backend** — DirectML for images (rock-solid on any GPU), ZLUDA for photoreal video (opt-in)
- **ComfyUI** under the hood, wrapped in a polished Tauri + React desktop app
- **AMD-optimized** for the RX 7900 XT (20 GB VRAM exploited fully)
- **Modes**: Text-to-Image, Image-to-Image, Inpainting, Upscaling, **Video Pro** (LTX-Video, Wan 2.1, Hunyuan)
- **Model support**: SDXL, SD 1.5, Flux.1 (dev/schnell), AnimateDiff, custom checkpoints, LoRAs
- **Presets**: Photorealistic, Cinematic, Anime, plus Fast / Balanced / Quality tiers
- **Queue, drag-and-drop, gallery with metadata, dark modern UI**
- **Portable mode** — runs from a USB drive, zero registry writes
- **Auto-updater** with offline opt-out

## What's new in 1.1.0 — Video Pro

The big addition: **photorealistic AI video generation**, fully local.

Out of the box you get DirectML image generation. With one click in the new **Video Pro** tab, LocalForge downloads a second, isolated backend that uses [ZLUDA](https://github.com/lshqqytiger/ZLUDA) to run CUDA-only video models on AMD GPUs:

| Model            | Resolution | Frames | VRAM  | Speed   | Best for                  |
| ---------------- | ---------- | ------ | ----- | ------- | ------------------------- |
| **LTX-Video**    | 768×512    | 121    | 12 GB | ★★★★★   | Fast iteration (default)  |
| **Wan 2.1 T2V**  | 832×480    | 81     | 14 GB | ★★★★    | Best quality/speed ratio  |
| **Hunyuan Video**| 1280×720   | 129    | 18 GB | ★★      | Maximum quality on 7900XT |

The image and video backends run side-by-side on separate ports — you can queue images on the image backend while a video renders on the video backend without interference.

See [docs/VIDEO_PRO.md](docs/VIDEO_PRO.md) for the full guide.

## Quick Start

1. Download `LocalForge-Setup-1.1.0.exe` from the [Releases page](#).
2. Run it. Click **Next → Next → Install → Finish**.
3. On first launch, choose a model from the Welcome screen (or skip and add your own later).
4. Type a prompt. Click **Generate**. That's it.

> First launch downloads ~7 GB of base image models. After that, image generation is fully offline.
> Want video too? Open the **Video Pro** tab inside the app and click Install (~6 GB, one-time).

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Model Installation](docs/MODELS.md)
- [GPU Optimization](docs/GPU_OPTIMIZATION.md)
- **[Video Pro Mode](docs/VIDEO_PRO.md)** ← new
- [Portable Build](docs/PORTABLE.md)
- [Workflows](docs/WORKFLOWS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Auto-Update](docs/AUTO_UPDATE.md)
- [Building from Source](docs/BUILD.md)

## License

MIT — do what you want with it.
