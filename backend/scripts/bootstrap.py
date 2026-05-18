"""First-run setup. Idempotent.

Steps:
  1. Make sure the embedded Python (backend/python/) exists.
  2. Clone/extract ComfyUI into backend/comfyui/ if missing.
  3. Install Python dependencies into the embedded interpreter.
  4. Install torch-directml.
  5. Symlink the user's models/ dir into comfyui/models/.

Designed to be invoked silently from the NSIS installer post-install action
and also runnable manually (`python bootstrap.py`).
"""
from __future__ import annotations
import os, subprocess, sys, urllib.request, zipfile, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent       # backend/
PYDIR = ROOT / "python"
COMFY = ROOT / "comfyui"
REQ = ROOT / "requirements.txt"

EMBED_PY_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
COMFY_ZIP = "https://github.com/comfyanonymous/ComfyUI/archive/refs/heads/master.zip"


def run(cmd: list[str], **kw) -> None:
    print(">>", " ".join(map(str, cmd)))
    subprocess.check_call(cmd, **kw)


def fetch(url: str, dest: Path) -> None:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dest)


def install_python() -> None:
    if (PYDIR / "python.exe").exists(): return
    PYDIR.mkdir(parents=True, exist_ok=True)
    tmp = PYDIR / "embed.zip"
    fetch(EMBED_PY_URL, tmp)
    with zipfile.ZipFile(tmp) as z: z.extractall(PYDIR)
    tmp.unlink()

    # Enable site-packages in embeddable python
    pth = next(PYDIR.glob("python*._pth"))
    txt = pth.read_text().replace("#import site", "import site")
    pth.write_text(txt)

    # Install pip
    getpip = PYDIR / "get-pip.py"
    fetch("https://bootstrap.pypa.io/get-pip.py", getpip)
    run([str(PYDIR / "python.exe"), str(getpip)])
    getpip.unlink()


def install_comfyui() -> None:
    if (COMFY / "main.py").exists(): return
    tmp = ROOT / "comfy.zip"
    fetch(COMFY_ZIP, tmp)
    with zipfile.ZipFile(tmp) as z: z.extractall(ROOT)
    # Move ComfyUI-master/ → comfyui/
    src = ROOT / "ComfyUI-master"
    if src.exists():
        if COMFY.exists(): shutil.rmtree(COMFY)
        src.rename(COMFY)
    tmp.unlink()


def install_python_deps() -> None:
    py = PYDIR / "python.exe"
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "-r", str(REQ)])
    # ComfyUI's own requirements
    if (COMFY / "requirements.txt").exists():
        run([str(py), "-m", "pip", "install", "-r", str(COMFY / "requirements.txt")])


def install_directml() -> None:
    py = PYDIR / "python.exe"
    # Torch CPU + torch-directml. The DirectML wheel bundles the DirectX backend.
    run([str(py), "-m", "pip", "install",
         "torch==2.3.1", "torchvision==0.18.1",
         "--index-url", "https://download.pytorch.org/whl/cpu"])
    run([str(py), "-m", "pip", "install", "torch-directml"])


def link_models() -> None:
    """Replace comfyui/models with a junction pointing to %APPDATA%/LocalForge/models."""
    data_dir = Path(os.environ.get("LOCALFORGE_DATA_DIR",
                                   Path(os.environ["APPDATA"]) / "LocalForge"))
    models_dir = data_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    target = COMFY / "models"
    if target.exists() and not target.is_symlink():
        # If ComfyUI ships a default models dir, move it aside
        shutil.rmtree(target, ignore_errors=True)
    if not target.exists():
        # Windows directory junction (no admin needed)
        subprocess.check_call(["cmd", "/c", "mklink", "/J", str(target), str(models_dir)])


def main() -> None:
    print("=== LocalForge bootstrap ===")
    install_python()
    install_comfyui()
    install_python_deps()
    install_directml()
    link_models()
    print("=== Done ===")


if __name__ == "__main__":
    main()
