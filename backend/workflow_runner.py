"""Runs ComfyUI workflows and streams progress back to the queue."""
from __future__ import annotations
import asyncio, json, uuid
import httpx, websockets
from preset_engine import build as build_workflow
from queue_manager import QUEUE, Job
from config import SETTINGS, OUTPUT_DIR
from gallery import register_output
from backends import route_port


def _http(port: int) -> str: return f"http://127.0.0.1:{port}"
def _ws(port: int) -> str: return f"ws://127.0.0.1:{port}/ws"


async def _post_prompt(workflow: dict, client_id: str, port: int) -> str:
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{_http(port)}/prompt",
                         json={"prompt": workflow, "client_id": client_id})
        r.raise_for_status()
        return r.json()["prompt_id"]


async def _get_history(prompt_id: str, port: int) -> dict:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{_http(port)}/history/{prompt_id}")
        r.raise_for_status()
        return r.json().get(prompt_id, {})


async def _download_image(filename: str, subfolder: str, type_: str, port: int) -> bytes:
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(f"{_http(port)}/view",
                        params={"filename": filename, "subfolder": subfolder, "type": type_})
        r.raise_for_status()
        return r.content


async def run_job(job: Job) -> None:
    """Build a workflow, send it to the correct ComfyUI backend, stream progress."""
    try:
        port = route_port(job.params.get("mode", "txt2img"))
        wf = build_workflow(job.params)
        client_id = uuid.uuid4().hex
        prompt_id = await _post_prompt(wf, client_id, port)

        async with websockets.connect(f"{_ws(port)}?clientId={client_id}", max_size=8 * 1024 * 1024) as ws:
            while True:
                if job.status == "cancelled":
                    return
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=600)
                except asyncio.TimeoutError:
                    raise RuntimeError("ComfyUI timed out (10 min)")

                if isinstance(msg, bytes):
                    # Preview frame (latent/PNG bytes) — skip in MVP
                    continue
                data = json.loads(msg)
                t = data.get("type")
                if t == "progress":
                    p = data["data"]["value"] / max(1, data["data"]["max"])
                    await QUEUE.update(job.id, progress=p)
                elif t == "executing" and data["data"]["node"] is None and data["data"]["prompt_id"] == prompt_id:
                    break  # finished

        # Collect outputs (images AND videos)
        history = await _get_history(prompt_id, port)
        out_files: list[str] = []
        for node_out in history.get("outputs", {}).values():
            for item in (node_out.get("images", []) + node_out.get("gifs", []) + node_out.get("videos", [])):
                blob = await _download_image(item["filename"], item.get("subfolder", ""), item.get("type", "output"), port)
                target = OUTPUT_DIR / item["filename"]
                target.write_bytes(blob)
                register_output(target, job.params)
                out_files.append(item["filename"])

        await QUEUE.update(job.id, status="done", progress=1.0, result=out_files)
    except Exception as e:
        await QUEUE.update(job.id, status="error", error=str(e))


async def worker_loop() -> None:
    """Single-worker loop; the GPU is serial anyway."""
    while True:
        job = await QUEUE.next_runnable()
        await run_job(job)
