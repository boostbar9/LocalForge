from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from config import OUTPUT_DIR
from gallery import list_items

router = APIRouter()


@router.get("/api/gallery")
async def gallery(limit: int = Query(100, le=500), offset: int = 0):
    return list_items(limit=limit, offset=offset)


@router.get("/api/image/{filename}")
async def serve_image(filename: str):
    p = (OUTPUT_DIR / filename).resolve()
    # Path traversal guard
    if not str(p).startswith(str(OUTPUT_DIR.resolve())):
        return JSONResponse({"error": "invalid path"}, status_code=400)
    if not p.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(p)


@router.get("/api/reveal")
async def reveal(file: str):
    import subprocess
    p = (OUTPUT_DIR / file).resolve()
    if str(p).startswith(str(OUTPUT_DIR.resolve())) and p.exists():
        subprocess.Popen(["explorer", "/select,", str(p)])
    return {"ok": True}
