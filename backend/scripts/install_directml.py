"""Standalone DirectML reinstall — used by the Settings page 'Repair GPU backend' button."""
import subprocess, sys
from pathlib import Path

PY = Path(__file__).resolve().parent.parent / "python" / "python.exe"

def main():
    subprocess.check_call([str(PY), "-m", "pip", "install", "--force-reinstall",
                           "torch==2.3.1", "torchvision==0.18.1",
                           "--index-url", "https://download.pytorch.org/whl/cpu"])
    subprocess.check_call([str(PY), "-m", "pip", "install", "--force-reinstall", "torch-directml"])

if __name__ == "__main__":
    main()
