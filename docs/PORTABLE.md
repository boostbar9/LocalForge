# Portable Build

LocalForge runs in fully portable mode when a file named **`portable.txt`** exists in the same folder as `LocalForge.exe`.

In portable mode:
- All models, output, logs, and settings live under `localforge_data\` next to the EXE
- No registry writes
- No `%APPDATA%` usage
- Can be carried on a USB stick or external SSD

## Building a portable distribution

From a Windows machine with the source tree:

```powershell
# 1. Build the frontend + Tauri shell in release mode
cd LocalForge\src-tauri
cargo build --release

# 2. Package portable bundle
cd ..\installer\portable
.\make_portable.ps1 -Version 1.0.0
```

The script produces `installer\portable\dist\LocalForge-1.0.0-portable.zip`. It:

1. Copies `LocalForge.exe` from the Tauri build
2. Bundles the `backend/` directory (Python + ComfyUI + workflows)
3. Adds the `portable.txt` marker
4. **Pre-runs `bootstrap.py`** so the end user doesn't wait 5-10 minutes on first launch
5. Zips with maximum LZMA compression (~2.1 GB final size)

## Pre-loading models into the portable bundle

If you want to ship a bundle that's ready to generate offline immediately:

```powershell
# After bootstrap, drop checkpoints into models/ before zipping
$bundle = ".\dist\LocalForge-1.0.0-portable"
Copy-Item "C:\my-models\sd_xl_base_1.0.safetensors" `
          "$bundle\localforge_data\models\checkpoints\"
```

Then re-zip. End users unzipping the bundle can generate immediately with zero network access.

## Using the portable build

1. Unzip the bundle to anywhere — USB, external SSD, Desktop, network share.
2. Double-click `LocalForge.exe`.
3. That's it.

## Air-gapped operation

In LocalForge: **Settings → Privacy → Block ALL outbound network**.

Once toggled on, the backend refuses any HTTP/HTTPS request (model downloads, update checks). Combined with portable mode and pre-loaded models, you get a fully sealed offline environment suitable for sensitive workflows.
