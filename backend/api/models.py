from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import subprocess
from model_manager import list_installed, download_recommended
from config import MODELS_DIR

router = APIRouter()


@router.get("/api/models")
async def models():
    return list_installed()


class DownloadReq(BaseModel):
    id: str


@router.post("/api/models/download")
async def download(req: DownloadReq, bg: BackgroundTasks):
    bg.add_task(download_recommended, req.id)
    return {"queued": True, "id": req.id}


@router.get("/api/models/open_folder")
async def open_folder():
    subprocess.Popen(["explorer", str(MODELS_DIR)])
    return {"ok": True}
