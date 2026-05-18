# Example Workflows

LocalForge ships seven prebuilt ComfyUI workflows. Each is a JSON node graph
in `backend/workflows/`, patched at runtime by `preset_engine.py` with the
user's prompt, size, steps, and chosen model.

## Built-in workflows

| File | Purpose | Frontend mode |
|---|---|---|
| `sdxl_txt2img.json` | SDXL text-to-image | Text → Image |
| `sdxl_img2img.json` | SDXL image-to-image, default denoise 0.55 | Image → Image |
| `sdxl_inpaint.json` | SDXL inpainting with mask, grow_mask_by=6 | Inpaint |
| `flux_txt2img.json` | Flux Schnell 4-step generation, cfg=1 | Text → Image (Flux style) |
| `upscale_4x.json` | Real-ESRGAN 4x upscale | Upscale |
| `restore_face.json` | CodeFormer face restoration | Upscale |
| `animatediff_txt2vid.json` | AnimateDiff v3, 16 frames @ 8 fps | Text → Video |

## How the preset engine patches them

Each template carries a `_lf` metadata block identifying the node IDs to patch:

```json
"_lf": {
  "positive_node": "6",
  "negative_node": "7",
  "sampler_node": "3",
  "latent_node": "5",
  "checkpoint_node": "4"
}
```

When a user clicks Generate, `preset_engine.build()`:

1. Loads the template
2. Composes the final prompt: `<user prompt>, <style tag bundle>`
3. Patches the CLIP text encoders
4. Sets `steps` and `cfg` from the **Quality** tier
5. Sets `width`, `height`, `batch_size` on the latent node
6. Sets the checkpoint name on the loader node
7. Strips `_lf` and POSTs the graph to ComfyUI's `/prompt` endpoint

## Adding your own workflow

1. Export from the ComfyUI desktop UI: **Save (API Format)**.
2. Drop the file in `backend/workflows/my_workflow.json`.
3. Add a `_lf` block identifying which nodes hold the prompt/sampler/latent/checkpoint.
4. Register it in `preset_engine.py`'s `wf_name` dispatch table.
5. Restart LocalForge.

## Image-to-Image example

The `sdxl_img2img.json` graph:

```
LoadImage → VAEEncode ──┐
                        ▼
CLIPTextEncode (pos) → KSampler → VAEDecode → SaveImage
CLIPTextEncode (neg) ──┘            ▲
                       CheckpointLoaderSimple
```

The denoise strength (0.55 default) controls how much of the input is preserved:
- 0.30 → light style transfer
- 0.55 → moderate reinterpretation (default)
- 0.85 → almost free-form, input is only a seed

## Video generation example

The AnimateDiff graph generates 16 frames at 768×768, combined into an MP4 by
`VHS_VideoCombine` at 8 fps (~2 seconds of video). On the RX 7900 XT this takes
roughly 90 seconds per clip.

Tuning knobs:
- `batch_size` in node `5` = number of frames
- `frame_rate` in node `30` = playback fps
- `width`/`height` in node `5` — keep ≤ 768 for memory safety
