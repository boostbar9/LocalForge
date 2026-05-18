# Building from Source

For developers. End users should use the installer.

## Prerequisites

| Tool | Version |
|---|---|
| Windows | 10/11 x64 |
| Node.js | 18+ |
| Rust | 1.78+ via [rustup](https://rustup.rs) |
| Python | 3.11 (the embedded one is fetched automatically) |
| Visual Studio Build Tools | "Desktop development with C++" workload |
| NSIS | 3.09+ (only for the standalone installer) |

## One-time setup

```bash
git clone https://github.com/your-fork/LocalForge.git
cd LocalForge

# Frontend deps
cd frontend && npm install && cd ..

# Tauri CLI
cargo install tauri-cli --version "^1.6"

# Bootstrap Python backend (downloads embeddable Python + ComfyUI + DirectML)
python backend/scripts/bootstrap.py
```

## Dev loop

```bash
# 1. Frontend (Vite hot reload)
cd frontend && npm run dev &

# 2. Backend (auto-reload on file change)
python backend/main.py

# 3. Tauri shell (opens window, hot-reloads frontend)
cargo tauri dev
```

## Production build

```bash
cargo tauri build
```

Output:
- `src-tauri/target/release/LocalForge.exe`
- `src-tauri/target/release/bundle/nsis/LocalForge_1.0.0_x64-setup.exe`

## Switching to ZLUDA (for advanced users)

```powershell
# 1. Remove DirectML wheel
backend\python\python.exe -m pip uninstall -y torch torch-directml torchvision

# 2. Install CUDA-built PyTorch
backend\python\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 3. Drop ZLUDA DLLs next to python.exe
#    - Download ZLUDA v3 from https://github.com/lshqqytiger/ZLUDA
#    - Copy nvcuda.dll, nvml.dll, cublas.dll to backend\python\

# 4. Update backend/gpu_detect.py:
#    Change `args += ["--directml"]` to `args += []`
```

Expect ~50% speed boost on the 7900 XT, with occasional model incompatibilities.
