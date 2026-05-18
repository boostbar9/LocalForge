# Project Structure

```
LocalForge/
├── README.md
├── LICENSE
├── PROJECT_STRUCTURE.md
│
├── src-tauri/                    # Rust Tauri shell
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── build.rs
│   ├── icons/                    # App icons (ico/png)
│   └── src/
│       ├── main.rs               # Entry, spawns backend
│       ├── backend.rs            # Child-process supervisor
│       ├── updater.rs            # Auto-update logic
│       └── commands.rs           # IPC commands exposed to JS
│
├── frontend/                     # React + Vite UI
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── lib/
│       │   ├── api.ts            # Backend client
│       │   ├── ws.ts             # WebSocket progress
│       │   └── presets.ts        # Preset definitions
│       ├── components/
│       │   ├── Sidebar.tsx
│       │   ├── PromptBox.tsx
│       │   ├── PresetSelector.tsx
│       │   ├── GalleryGrid.tsx
│       │   ├── QueuePanel.tsx
│       │   ├── DropZone.tsx
│       │   ├── ImageViewer.tsx
│       │   ├── ProgressBar.tsx
│       │   └── ModelPicker.tsx
│       ├── pages/
│       │   ├── Generate.tsx
│       │   ├── Gallery.tsx
│       │   ├── Models.tsx
│       │   ├── Queue.tsx
│       │   ├── Settings.tsx
│       │   └── Welcome.tsx
│       └── styles/
│           └── globals.css
│
├── backend/                      # Python backend
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── main.py                   # FastAPI entry
│   ├── config.py
│   ├── gpu_detect.py             # Auto GPU detection
│   ├── queue_manager.py          # SQLite-backed job queue
│   ├── workflow_runner.py        # ComfyUI client
│   ├── model_manager.py          # Downloads, hashing, folder mgmt
│   ├── preset_engine.py          # Preset → workflow JSON
│   ├── gallery.py                # Image index + metadata
│   ├── api/
│   │   ├── __init__.py
│   │   ├── generate.py
│   │   ├── gallery.py
│   │   ├── models.py
│   │   ├── settings.py
│   │   └── ws.py
│   ├── workflows/                # ComfyUI workflow templates
│   │   ├── sdxl_txt2img.json
│   │   ├── sdxl_img2img.json
│   │   ├── sdxl_inpaint.json
│   │   ├── flux_txt2img.json
│   │   ├── animatediff_txt2vid.json
│   │   ├── upscale_4x.json
│   │   └── restore_face.json
│   ├── presets/
│   │   ├── photorealistic.json
│   │   ├── cinematic.json
│   │   ├── anime.json
│   │   ├── quality_fast.json
│   │   ├── quality_balanced.json
│   │   └── quality_max.json
│   ├── scripts/
│   │   ├── bootstrap.py          # First-run setup
│   │   ├── install_comfyui.py
│   │   ├── install_directml.py
│   │   └── download_models.py
│   └── comfyui/                  # Vendored at install time (.gitignore)
│
├── installer/
│   ├── nsis/
│   │   └── localforge.nsi        # NSIS installer script
│   ├── portable/
│   │   └── make_portable.ps1
│   └── update_manifest.example.json
│
├── resources/
│   ├── icon.ico
│   ├── icon.png
│   └── splash.png
│
└── docs/
    ├── SETUP.md
    ├── MODELS.md
    ├── GPU_OPTIMIZATION.md
    ├── PORTABLE.md
    ├── ARCHITECTURE.md
    ├── AUTO_UPDATE.md
    ├── BUILD.md
    └── WORKFLOWS.md
```
