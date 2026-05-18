# Model Installation

LocalForge stores models under:

- **Installed mode:** `%APPDATA%\LocalForge\models\`
- **Portable mode:** `localforge_data\models\` next to `LocalForge.exe`

Folder layout:

```
models/
├── checkpoints/         # SDXL, SD 1.5, Flux full models (.safetensors)
├── loras/               # LoRAs (.safetensors)
├── vaes/                # Optional standalone VAEs
├── upscale_models/      # ESRGAN, RealESRGAN, 4xUltrasharp
├── animatediff_models/  # Motion modules for video
├── controlnet/          # ControlNet checkpoints
├── clip/                # CLIP encoders (Flux needs these)
├── clip_vision/         # CLIP vision (IP-Adapter)
└── embeddings/          # Textual inversion embeddings
```

## One-click downloads (Models page)

| Model | Size | Purpose |
|---|---|---|
| Stable Diffusion XL 1.0 base | 6.9 GB | Default general-purpose |
| RealVisXL V4.0 | 6.5 GB | Photoreal preset default |
| Animagine XL 3.1 | 6.9 GB | Anime preset default |
| Flux.1 Schnell | 12.5 GB | High fidelity, 4-step generation |
| Real-ESRGAN x4plus | 63 MB | Upscaler |
| AnimateDiff v3 motion module | 1.7 GB | Text-to-video |

Click **Get** in the Models tab — files stream into the right subfolder.

## Adding your own models

Just drop them into the right subfolder. No restart required — the Models page **Refresh** button rescans the disk.

### Common sources

- [HuggingFace](https://huggingface.co/) — official repos
- [Civitai](https://civitai.com/) — community fine-tunes and LoRAs
- Your own training output

### File compatibility

| Extension | Use |
|---|---|
| `.safetensors` | Preferred — safe, fast |
| `.ckpt` | Legacy SD format |
| `.gguf` | Flux quantized variants |
| `.pt`, `.pth` | LoRAs / upscalers |

## VRAM guidance for the RX 7900 XT (20 GB)

You can run any of these comfortably:

- SDXL @ 1216×832, batch 4
- Flux Schnell @ 1024×1024, batch 1
- AnimateDiff @ 768×768, 16 frames

If you push higher resolutions and see out-of-memory errors, switch **Settings → VRAM mode** to **Balanced**.

## Removing a model

Either delete the file from the folder, or use **Models → Open models folder → Delete**. The next refresh will drop it from the dropdown.
