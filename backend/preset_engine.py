"""Translate a user-facing preset (e.g. {style: "photoreal", quality: "balanced"})
into a concrete ComfyUI workflow graph by loading the matching template and
patching nodes (prompt, size, steps, seed, model, etc.).
"""
from __future__ import annotations
import copy, json, random
from pathlib import Path
from typing import Any

WORKFLOWS_DIR = Path(__file__).parent / "workflows"
PRESETS_DIR = Path(__file__).parent / "presets"

# Quality → step count
QUALITY_STEPS = {"fast": 20, "balanced": 30, "max": 50}
QUALITY_CFG = {"fast": 4.5, "balanced": 6.0, "max": 7.5}

# Style → positive/negative tag bundle
STYLE_TAGS = {
    "photorealistic": {
        "positive": "raw photo, photorealistic, sharp focus, natural lighting, "
                    "skin texture, depth of field, 50mm, 8k",
        "negative": "cartoon, illustration, painting, drawing, anime, render, "
                    "cgi, plastic skin, low quality, blurry, watermark, text",
    },
    "cinematic": {
        "positive": "cinematic still, anamorphic lens flare, film grain, "
                    "dramatic lighting, color graded teal and orange, shallow depth of field",
        "negative": "amateur, low quality, blurry, oversharpened, watermark",
    },
    "anime": {
        "positive": "anime, masterpiece, best quality, vibrant colors, clean lineart, "
                    "detailed eyes, screentone, soft cel shading",
        "negative": "photo, photorealistic, 3d render, deformed, lowres, jpeg artifacts, watermark",
    },
    "flux_default": {
        "positive": "high detail, professional photography, natural composition",
        "negative": "",  # Flux prefers no negative prompt
    },
}


def _load_workflow(name: str) -> dict:
    p = WORKFLOWS_DIR / f"{name}.json"
    return json.loads(p.read_text())


def _find_node(wf: dict, class_type: str) -> str | None:
    for nid, node in wf.items():
        if node.get("class_type") == class_type:
            return nid
    return None


def _set_text(wf: dict, node_id: str, text: str) -> None:
    wf[node_id]["inputs"]["text"] = text


VIDEO_MODEL_TO_WORKFLOW = {
    "ltx": "ltx_video_txt2vid",
    "wan21": "wan21_txt2vid",
    "hunyuan": "hunyuan_txt2vid",
    "animatediff": "animatediff_txt2vid",
}


def build(params: dict) -> dict:
    """Convert frontend params to a ComfyUI workflow."""
    mode = params.get("mode", "txt2img")
    preset = params.get("preset", "photorealistic")
    quality = params.get("quality", "balanced")
    family = "flux" if preset.startswith("flux") else "sdxl"

    # Video mode: route by selected video model
    if mode in ("txt2vid", "img2vid"):
        vmodel = params.get("video_model", "ltx")
        wf_name = VIDEO_MODEL_TO_WORKFLOW.get(vmodel, "ltx_video_txt2vid")
    else:
        wf_name = {
            ("sdxl", "txt2img"): "sdxl_txt2img",
            ("sdxl", "img2img"): "sdxl_img2img",
            ("sdxl", "inpaint"): "sdxl_inpaint",
            ("sdxl", "upscale"): "upscale_4x",
            ("flux", "txt2img"): "flux_txt2img",
            ("flux", "img2img"): "sdxl_img2img",
            ("flux", "inpaint"): "sdxl_inpaint",
            ("flux", "upscale"): "upscale_4x",
        }[(family, mode)]

    wf = copy.deepcopy(_load_workflow(wf_name))

    # Compose prompt with style tags
    tags = STYLE_TAGS.get(preset, STYLE_TAGS["photorealistic"])
    user_prompt = params.get("prompt", "").strip()
    user_neg = params.get("negative_prompt", "").strip()
    final_pos = f"{user_prompt}, {tags['positive']}" if user_prompt else tags["positive"]
    final_neg = ", ".join([t for t in [user_neg, tags["negative"]] if t])

    # Patch CLIP text encoders (assumes nodes labeled in templates)
    pos_id = wf.get("_lf").get("positive_node") if "_lf" in wf else None
    neg_id = wf.get("_lf", {}).get("negative_node")
    sampler_id = wf.get("_lf", {}).get("sampler_node")
    latent_id = wf.get("_lf", {}).get("latent_node")
    ckpt_id = wf.get("_lf", {}).get("checkpoint_node")

    if pos_id:
        _set_text(wf, pos_id, final_pos)
    if neg_id and final_neg:
        _set_text(wf, neg_id, final_neg)

    # Steps / CFG / seed
    if sampler_id:
        seed = params.get("seed") or random.randint(0, 2**32 - 1)
        wf[sampler_id]["inputs"]["steps"] = params.get("steps") or QUALITY_STEPS[quality]
        wf[sampler_id]["inputs"]["cfg"] = params.get("cfg") or QUALITY_CFG[quality]
        wf[sampler_id]["inputs"]["seed"] = int(seed)

    # Size
    if latent_id:
        wf[latent_id]["inputs"]["width"] = int(params.get("width", 1024))
        wf[latent_id]["inputs"]["height"] = int(params.get("height", 1024))
        wf[latent_id]["inputs"]["batch_size"] = int(params.get("count", 1))

    # Custom checkpoint
    if ckpt_id and params.get("model"):
        wf[ckpt_id]["inputs"]["ckpt_name"] = params["model"]

    # Strip metadata before sending
    wf.pop("_lf", None)
    return wf
