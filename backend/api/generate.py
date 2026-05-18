from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from queue_manager import QUEUE

router = APIRouter()


class GenerateRequest(BaseModel):
    mode: str = "txt2img"
    prompt: str = ""
    negative_prompt: str = ""
    preset: str = "photorealistic"
    quality: str = "balanced"
    width: int = 1024
    height: int = 1024
    steps: Optional[int] = None
    cfg: Optional[float] = None
    seed: Optional[int] = None
    model: Optional[str] = None
    lora: List[dict] = []
    init_image: Optional[str] = None
    mask: Optional[str] = None
    count: int = 1


@router.post("/api/generate")
async def generate(req: GenerateRequest):
    job = await QUEUE.enqueue(req.model_dump())
    return {"id": job.id}


@router.get("/api/jobs")
async def jobs():
    from dataclasses import asdict
    return [asdict(j) for j in QUEUE.list()]


@router.post("/api/jobs/{job_id}/cancel")
async def cancel(job_id: str):
    await QUEUE.cancel(job_id)
    return {"ok": True}
