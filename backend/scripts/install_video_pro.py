"""Install the Video Pro backend (ZLUDA + CUDA torch + ComfyUI clone + video nodes).

This runs only when the user clicks **Install Video Pro** in Settings.
Total download is ~3.5 GB; takes 5-15 minutes on a typical connection.

Steps:
  1. Fetch a SECOND embeddable Python (kept separate so DirectML torch stays untouched)
  2. Fetch ZLUDA v3 DLLs (nvcuda.dll, nvml.dll, cublas.dll, cusparse.dll)
  3. Install CUDA-built PyTorch into the second python
  4. Clone a SECOND ComfyUI for video work
  5. Install ComfyUI-VideoHelperSuite, ComfyUI-LTXVideo, ComfyUI-WanVideoWrapper
  6. Symlink models/ from the main install
  7. Verify torch.cuda.is_available() returns True via ZLUDA shim
"""
from __future__ import annotations
import os, shutil, subprocess, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent       # backend/
PYDIR = ROOT / "python_video"
COMFY = ROOT / "comfyui_video"
ZLUDA = ROOT / "zluda"

EMBED_PY_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
COMFY_ZIP   = "https://github.com/comfyanonymous/ComfyUI/archive/refs/heads/master.zip"
ZLUDA_ZIP   = "https://github.com/lshqqytiger/ZLUDA/releases/latest/download/ZLUDA-windows-amd64.zip"

VIDEO_NODES = [
    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/archive/refs/heads/main.zip",
    "https://github.com/Lightricks/ComfyUI-LTXVideo/archive/refs/heads/main.zip",
    "https://github.com/kijai/ComfyUI-WanVideoWrapper/archive/refs/heads/main.zip",
    "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper/archive/refs/heads/main.zip",
]


def run(cmd: list[str], **kw) -> None:
    print(">>", " ".join(map(str, cmd)))
    subprocess.check_call(cmd, **kw)


def fetch(url: str, dest: Path) -> None:
    print(f"↓ {url}")
    urllib.request.urlretrieve(url, dest)


def install_python() -> None:
    if (PYDIR / "python.exe").exists():
        return
    PYDIR.mkdir(parents=True, exist_ok=True)
    tmp = PYDIR / "embed.zip"
    fetch(EMBED_PY_URL, tmp)
    with zipfile.ZipFile(tmp) as z: z.extractall(PYDIR)
    tmp.unlink()
    pth = next(PYDIR.glob("python*._pth"))
    pth.write_text(pth.read_text().replace("#import site", "import site"))
    getpip = PYDIR / "get-pip.py"
    fetch("https://bootstrap.pypa.io/get-pip.py", getpip)
    run([str(PYDIR / "python.exe"), str(getpip)])
    getpip.unlink()


def install_zluda() -> None:
    if (ZLUDA / "nvcuda.dll").exists():
        return
    ZLUDA.mkdir(parents=True, exist_ok=True)
    tmp = ZLUDA / "zluda.zip"
    fetch(ZLUDA_ZIP, tmp)
    with zipfile.ZipFile(tmp) as z: z.extractall(ZLUDA)
    tmp.unlink()
    # Flatten if a nested folder was extracted
    inner = next((p for p in ZLUDA.iterdir() if p.is_dir() and (p / "nvcuda.dll").exists()), None)
    if inner:
        for f in inner.iterdir():
            shutil.move(str(f), str(ZLUDA))
        inner.rmdir()


def install_cuda_torch() -> None:
    """Install CUDA-built torch into the video Python. ZLUDA translates CUDA calls
    to ROCm/HIP at runtime, so this is the correct wheel — NOT the DirectML one."""
    py = PYDIR / "python.exe"
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install",
         "torch==2.3.1", "torchvision==0.18.1", "torchaudio==2.3.1",
         "--index-url", "https://download.pytorch.org/whl/cu118"])


def install_comfyui_video() -> None:
    if (COMFY / "main.py").exists():
        return
    tmp = ROOT / "comfy_video.zip"
    fetch(COMFY_ZIP, tmp)
    with zipfile.ZipFile(tmp) as z: z.extractall(ROOT)
    src = ROOT / "ComfyUI-master"
    if src.exists():
        if COMFY.exists(): shutil.rmtree(COMFY)
        src.rename(COMFY)
    tmp.unlink()

    py = PYDIR / "python.exe"
    if (COMFY / "requirements.txt").exists():
        run([str(py), "-m", "pip", "install", "-r", str(COMFY / "requirements.txt")])


def install_video_custom_nodes() -> None:
    nodes_dir = COMFY / "custom_nodes"
    nodes_dir.mkdir(exist_ok=True)
    for url in VIDEO_NODES:
        name = url.rstrip("/").split("/")[-3]   # repo name
        target = nodes_dir / name
        if target.exists():
            continue
        tmp = nodes_dir / f"{name}.zip"
        fetch(url, tmp)
        with zipfile.ZipFile(tmp) as z: z.extractall(nodes_dir)
        tmp.unlink()
        extracted = next((p for p in nodes_dir.iterdir() if p.is_dir() and name.lower() in p.name.lower()), None)
        if extracted and extracted.name != name:
            extracted.rename(target)
        # Install per-node requirements
        req = target / "requirements.txt"
        if req.exists():
            try: run([str(PYDIR / "python.exe"), "-m", "pip", "install", "-r", str(req)])
            except subprocess.CalledProcessError as e: print(f"!! skipping {name} reqs: {e}")


def link_models() -> None:
    """Share models with the image backend."""
    main_models = ROOT / "comfyui" / "models"
    if not main_models.exists():
        return
    target = COMFY / "models"
    if target.exists() and not target.is_symlink():
        shutil.rmtree(target, ignore_errors=True)
    if not target.exists():
        subprocess.check_call(["cmd", "/c", "mklink", "/J", str(target), str(main_models)])


def verify() -> bool:
    """Test that ZLUDA + torch can see the GPU."""
    env = os.environ.copy()
    env["PATH"] = f"{ZLUDA};{env['PATH']}"
    try:
        out = subprocess.check_output(
            [str(PYDIR / "python.exe"), "-c",
             "import torch; print('cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')"],
            env=env, text=True, timeout=30,
        )
        print(out)
        return "cuda True" in out
    except Exception as e:
        print(f"verify failed: {e}")
        return False


def main() -> None:
    print("=== LocalForge Video Pro installer ===")
    install_python()
    install_zluda()
    install_cuda_torch()
    install_comfyui_video()
    install_video_custom_nodes()
    link_models()
    ok = verify()
    print("=== Video Pro installed ===" if ok else "!! Verification failed — see logs")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
