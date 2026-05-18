# Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       LocalForge.exe                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Tauri Shell (Rust, ~8 MB)               │   │
│  │  • Window mgmt   • IPC bridge  • Auto-updater       │   │
│  │  • Spawns backend on launch, kills on exit          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          React + Vite Frontend (webview)            │   │
│  │  • Generate page  • Gallery  • Settings             │   │
│  │  • Presets  • Drag-drop  • Queue UI                 │   │
│  └─────────────────────────────────────────────────────┘   │
│              ▲                                              │
│              │ HTTP/WebSocket (localhost only)              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     LocalForge Backend (Python 3.11, FastAPI)       │   │
│  │  • REST API   • Job queue   • Workflow loader       │   │
│  │  • Model manager   • Preset → workflow translator   │   │
│  └─────────────────────────────────────────────────────┘   │
│              ▲                                              │
│              │ embedded                                     │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       ComfyUI (headless, port 8188, local)          │   │
│  │  • torch-directml   • SDXL / Flux / AnimateDiff     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Layers

### 1. Tauri Shell (`src-tauri/`)
- Rust binary that hosts the webview, manages the window, and spawns/kills the Python backend as a child process.
- Implements the auto-updater (signed update manifests pulled from a static URL the user controls; can be disabled).
- Exposes a tiny IPC API to the frontend: `open_folder`, `pick_model`, `get_version`, etc.

### 2. Frontend (`frontend/`)
- React + Vite + TypeScript + Tailwind.
- Talks to the backend over `http://127.0.0.1:8765` only — never reaches the public internet.
- Pages: **Generate**, **Gallery**, **Models**, **Queue**, **Settings**.

### 3. Backend (`backend/`)
- FastAPI service on port `8765` (configurable).
- Responsibilities:
  - Translate friendly preset payloads into ComfyUI workflow graphs.
  - Manage the job queue (SQLite-backed for crash recovery).
  - Stream progress over WebSocket.
  - Manage model files in `models/` and validate sha256 on download.
  - Persist gallery metadata (PNG-info + JSON sidecar).
- Spawns ComfyUI on `127.0.0.1:8188` (private, bound to loopback).

### 4. ComfyUI (`backend/comfyui/`)
- Unmodified upstream ComfyUI vendored as a submodule.
- Patched at runtime to use `torch-directml` instead of CUDA.
- Workflows live in `backend/workflows/*.json` and are loaded on demand.

## Data Flow — single generation

```
User clicks Generate
        │
        ▼
Frontend POST /api/generate  { preset: "photoreal", prompt, ... }
        │
        ▼
Backend builds workflow JSON from preset template + user params
        │
        ▼
Backend POST /prompt → ComfyUI (job queued)
        │
        ▼
Backend opens WS to ComfyUI, forwards progress to Frontend WS
        │
        ▼
ComfyUI writes PNG to backend/output/
        │
        ▼
Backend writes sidecar JSON, indexes in SQLite, notifies Frontend
        │
        ▼
Frontend shows image in gallery
```

## Why this split?

- **Tauri** gives a 10 MB native shell instead of 150 MB Electron.
- **Backend in Python** is mandatory because ComfyUI and PyTorch are Python.
- **ComfyUI** as the actual diffusion engine is the most battle-tested, model-compatible, node-based option — perfect for prebuilt workflows.
- **Modular**: any layer can be swapped. Want to replace ComfyUI with InvokeAI? Only the backend's `workflow_runner.py` changes.
